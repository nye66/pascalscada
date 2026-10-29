program deltatest;
{ 自测台达驱动：地址映射 + Modbus TCP 帧编解码。通过子类公开受保护方法。 }
{$mode objfpc}{$H+}
uses SysUtils, Classes, commtypes, ProtocolTypes, Tag, DeltaDriver, DeltaTCP;

type
  TTestDriver = class(TDeltaTCPDriver)
  public
    function Enc(TagObj:TTagRec; ToWrite:TArrayOfDouble; var ResultLen:LongInt):BYTES;
    function Dec(pkg:TIOPacket; out values:TArrayOfDouble):TProtocolIOResult;
    function Addr(dev, address:LongInt):LongInt;
    function Crit(dev:LongInt):LongInt;
    function WireDev(func:Byte; address:LongInt):LongInt;
    procedure Norm(var tr:TTagRec);
  end;

var
  pass, fail:LongInt;

function TTestDriver.Enc(TagObj:TTagRec; ToWrite:TArrayOfDouble; var ResultLen:LongInt):BYTES;
begin
  Result := inherited EncodePkg(TagObj,ToWrite,ResultLen);
end;

function TTestDriver.Dec(pkg:TIOPacket; out values:TArrayOfDouble):TProtocolIOResult;
begin
  Result := inherited DecodePkg(pkg,values);
end;

function TTestDriver.Addr(dev, address:LongInt):LongInt;
begin
  Result := inherited DeviceAddress(dev,address);
end;

function TTestDriver.Crit(dev:LongInt):LongInt;
begin
  Result := inherited DeviceCritical(dev);
end;

function TTestDriver.WireDev(func:Byte; address:LongInt):LongInt;
begin
  Result := inherited DeviceIndexByWireAddress(func,address);
end;

procedure TTestDriver.Norm(var tr:TTagRec);
begin
  inherited NormalizeTagRec(tr);
end;

procedure Check(const name:string; cond:Boolean);
begin
  if cond then begin
    inc(pass);
    writeln('PASS: ', name);
  end else begin
    inc(fail);
    writeln('FAIL: ', name);
  end;
end;

procedure CheckBytes(const name:string; pkg:BYTES; const expect:array of Byte);
var
  i:LongInt;
  ok:Boolean;
begin
  ok := Length(pkg) = Length(expect);
  if ok then
    for i:=0 to High(expect) do
      if pkg[i] <> expect[i] then begin
        ok := false;
        break;
      end;
  if not ok then begin
    write('       got: ');
    for i:=0 to High(pkg) do
      write(IntToHex(pkg[i],2),' ');
    writeln;
  end;
  Check(name, ok);
end;

function MakeTR(astation, afunc, aaddress, asize:LongInt):TTagRec;
begin
  Result := Default(TTagRec);
  Result.ID := 0; Result.Station := astation; Result.Rack := 0; Result.Slot := 0;
  Result.Address := aaddress; Result.ReadFunction := afunc; Result.WriteFunction := afunc;
  Result.OffSet := 0; Result.File_DB := 0; Result.SubElement := 0; Result.Count := 0;
  Result.RealOffset := 0; Result.Retries := 0; Result.UpdateTime := 0;
  Result.Path := ''; Result.CallBack := nil; Result.Size := asize;
end;

function RespPkg(const req:array of Byte; const resp:array of Byte):TIOPacket;
var
  i:LongInt;
begin
  Result := Default(TIOPacket);
  SetLength(Result.BufferToWrite,Length(req));
  for i:=0 to High(req) do
    Result.BufferToWrite[i] := req[i];
  SetLength(Result.BufferToRead,Length(resp));
  for i:=0 to High(resp) do
    Result.BufferToRead[i] := resp[i];
  Result.WriteIOResult := iorOK;
  Result.ReadIOResult := iorOK;
end;

var
  drv:TTestDriver;
  pkg:BYTES;
  rl:LongInt;
  vals:TArrayOfDouble;
  ior:TProtocolIOResult;
  i:TTagRec;
  p:TIOPacket;
begin
  pass := 0;
  fail := 0;

  //===================== DVP 系列地址映射 =====================
  writeln('--- DVP series address map ---');
  drv := TTestDriver.Create(nil);
  Check('default series is DVP', drv.Series = dvsDvp);

  Check('D100 -> 4196',  drv.Addr(8,100) = 4096+100);
  Check('D5000 -> 37768',drv.Addr(8,5000) = 5000-4096+36864);
  Check('M100 -> 2148',  drv.Addr(0,100) = 2048+100);
  Check('M1600 -> 45120',drv.Addr(0,1600) = 1600-1536+45056);
  Check('X10(oct)->1032',drv.Addr(1,10) = 8+1024);      //八进制 10 = 8
  Check('X17(oct)->1039',drv.Addr(1,17) = 15+1024);     //八进制 17 = 15
  Check('Y7 -> 1287',    drv.Addr(2,7) = 7+1280);
  Check('S50 -> 50',     drv.Addr(3,50) = 50);
  Check('T10 -> 1546',   drv.Addr(4,10) = 10+1536);
  Check('C50 -> 3634',   drv.Addr(5,50) = 50+3584);
  Check('TD10 -> 1546',  drv.Addr(9,10) = 10+1536);
  Check('CD199 -> 3783', drv.Addr(10,199) = 199+3584);
  Check('SM not on DVP', not drv.DeviceSupportedBySeries(6));
  Check('critical M = 3584', drv.Crit(0) = 3584);
  Check('critical D = 8192', drv.Crit(8) = 8192);
  Check('critical S = 0',    drv.Crit(3) = 0);

  //wire 反查：功能码 3 + 地址 4196 -> D
  Check('wire dev fc3@4196 = D',  drv.WireDev(3,4196) = 8);
  Check('wire dev fc3@37000 = D', drv.WireDev(3,37000) = 8);   //D 扩展区
  Check('wire dev fc1@2148 = M',  drv.WireDev(1,2148) = 0);
  Check('wire dev fc1@45120 = M', drv.WireDev(1,45120) = 0);    //M 扩展区
  Check('wire dev fc2@1032 = X',  drv.WireDev(2,1032) = 1);

  //===================== DVP 帧：读 D100 2 个字 =====================
  writeln('--- DVP frames ---');
  i := MakeTR(1, DELTA_FUNC_D, 100, 2);
  drv.Norm(i);
  Check('normalized D100 addr = 4196', i.Address = 4196);
  pkg := drv.Enc(i,nil,rl);
  CheckBytes('read D100 x2 fc03', pkg, [$00,$00,$00,$00,$00,$06,$01,$03,$10,$64,$00,$02]);
  Check('expected answer len 13', rl = 13);

  //应答解析
  p := RespPkg(pkg, [$00,$00,$00,$00,$00,$07,$01,$03,$04,$12,$34,$00,$56]);
  ior := drv.Dec(p,vals);
  Check('read answer ioOk', ior = ioOk);
  Check('read answer 2 values', Length(vals) = 2);
  Check('value0 = 4660', Trunc(vals[0]) = $1234);
  Check('value1 = 86',   Trunc(vals[1]) = $0056);

  //读 M100 位 (wire 2148) fc01
  i := MakeTR(1, DELTA_FUNC_M, 100, 10);
  drv.Norm(i);
  pkg := drv.Enc(i,nil,rl);
  CheckBytes('read M100 x10 fc01', pkg, [$00,$01,$00,$00,$00,$06,$01,$01,$08,$64,$00,$0A]);

  //读 X（fc02）
  i := MakeTR(1, DELTA_FUNC_X, 0, 8);
  drv.Norm(i);
  pkg := drv.Enc(i,nil,rl);
  CheckBytes('read X0 x8 fc02', pkg, [$00,$02,$00,$00,$00,$06,$01,$02,$04,$00,$00,$08]);

  //位应答解析：10 个位 -> 2 字节 $B5,$01 = 1,0,1,0,1,1,0,1, 1,0,0,0,0,0,0,0
  i := MakeTR(1, DELTA_FUNC_M, 100, 10);
  drv.Norm(i);
  pkg := drv.Enc(i,nil,rl);
  p := RespPkg(pkg, [$00,$00,$00,$00,$00,$05,$01,$01,$02,$B5,$01]);
  ior := drv.Dec(p,vals);
  Check('bit answer ioOk', ior = ioOk);
  Check('bit value0 = 1', Trunc(vals[0]) = 1);
  Check('bit value1 = 0', Trunc(vals[1]) = 0);
  Check('bit value5 = 1', Trunc(vals[5]) = 1);
  Check('bit value8 = 1', Trunc(vals[8]) = 1);
  Check('bit value9 = 0', Trunc(vals[9]) = 0);

  //写单个位 M100=1 (fc05)
  SetLength(vals,1); vals[0] := 1;
  i := MakeTR(1, DELTA_FUNC_M, 100, 1);
  drv.Norm(i);
  pkg := drv.Enc(i,vals,rl);
  CheckBytes('write M100=1 fc05', pkg, [$00,$04,$00,$00,$00,$06,$01,$05,$08,$64,$FF,$00]);
  Check('write single coil answer len 12', rl = 12);
  //写应答回读
  p := RespPkg(pkg, [$00,$00,$00,$00,$00,$06,$01,$05,$08,$64,$FF,$00]);
  ior := drv.Dec(p,vals);
  Check('write coil ioOk', ior = ioOk);
  Check('write coil echo value 1', Trunc(vals[0]) = 1);

  //写单个字 D100=1234 (fc06)
  SetLength(vals,1); vals[0] := 1234;
  i := MakeTR(1, DELTA_FUNC_D, 100, 1);
  drv.Norm(i);
  pkg := drv.Enc(i,vals,rl);
  CheckBytes('write D100=1234 fc06', pkg, [$00,$05,$00,$00,$00,$06,$01,$06,$10,$64,$04,$D2]);
  p := RespPkg(pkg, [$00,$05,$00,$00,$00,$06,$01,$06,$10,$64,$04,$D2]);
  ior := drv.Dec(p,vals);
  Check('write reg ioOk', ior = ioOk);
  Check('write reg echo 1234', Trunc(vals[0]) = 1234);

  //多写位 M0..3 = [1,0,1,1] (fc0F)
  SetLength(vals,4); vals[0]:=1; vals[1]:=0; vals[2]:=1; vals[3]:=1;
  i := MakeTR(1, DELTA_FUNC_M, 0, 4);
  drv.Norm(i);
  pkg := drv.Enc(i,vals,rl);
  CheckBytes('write M0..3 fc0F', pkg, [$00,$06,$00,$00,$00,$08,$01,$0F,$08,$00,$00,$04,$01,$0D]);

  //多写字 D0..1 = [1000, 2000] (fc10)
  SetLength(vals,2); vals[0]:=1000; vals[1]:=2000;
  i := MakeTR(1, DELTA_FUNC_D, 0, 2);
  drv.Norm(i);
  pkg := drv.Enc(i,vals,rl);
  CheckBytes('write D0..1 fc10', pkg, [$00,$07,$00,$00,$00,$0B,$01,$10,$10,$00,$00,$02,$04,$03,$E8,$07,$D0]);
  p := RespPkg(pkg, [$00,$07,$00,$00,$00,$06,$01,$10,$10,$00,$00,$02]);
  ior := drv.Dec(p,vals);
  Check('write multi words ioOk', ior = ioOk);
  Check('write multi echo w0=1000', Trunc(vals[0]) = 1000);
  Check('write multi echo w1=2000', Trunc(vals[1]) = 2000);

  //异常应答：fc03|$80，异常码 02 -> ioIllegalRegAddress
  i := MakeTR(1, DELTA_FUNC_D, 100, 2);
  drv.Norm(i);
  pkg := drv.Enc(i,nil,rl);
  p := RespPkg(pkg, [$00,$00,$00,$00,$00,$03,$01,$83,$02]);
  ior := drv.Dec(p,vals);
  Check('exception 02 -> ioIllegalRegAddress', ior = ioIllegalRegAddress);

  //X 不可写：编码返回空
  SetLength(vals,1); vals[0] := 1;
  i := MakeTR(1, DELTA_FUNC_X, 0, 1);
  pkg := drv.Enc(i,vals,rl);
  Check('write X rejected (nil)', pkg = nil);

  //SM 在 DVP 上不可用：编码返回空
  i := MakeTR(1, DELTA_FUNC_SM, 0, 1);
  pkg := drv.Enc(i,nil,rl);
  Check('read SM on DVP rejected (nil)', pkg = nil);

  drv.Free;

  //===================== AS 系列地址映射 =====================
  writeln('--- AS series address map ---');
  drv := TTestDriver.Create(nil);
  drv.Series := dvsAS;
  Check('AS M100 -> 100',    drv.Addr(0,100) = 100);
  Check('AS SM10 -> 16394',  drv.Addr(6,10) = 10+16384);
  Check('AS S50 -> 20530',   drv.Addr(3,50) = 50+20480);
  Check('AS X20 -> 24596',   drv.Addr(1,20) = 20+24576);
  Check('AS Y20 -> 40980',   drv.Addr(2,20) = 20+40960);
  Check('AS T5 -> 57349',    drv.Addr(4,5) = 5+57344);
  Check('AS C5 -> 61445',    drv.Addr(5,5) = 5+61440);
  Check('AS HC5 -> 64517',   drv.Addr(7,5) = 5+64512);
  Check('AS D100 -> 100',    drv.Addr(8,100) = 100);
  Check('AS SR0 -> 49152',   drv.Addr(11,0) = 49152);
  Check('AS HCD0 -> 64512',  drv.Addr(12,0) = 64512);
  Check('AS E5 -> 65029',    drv.Addr(13,5) = 5+65024);
  Check('AS SM supported',   drv.DeviceSupportedBySeries(6));
  Check('AS no criticals',   drv.Crit(0) = 0);

  //AS 读 D100 2 个字（fc03，地址 100）
  i := MakeTR(1, DELTA_FUNC_D, 100, 2);
  drv.Norm(i);
  pkg := drv.Enc(i,nil,rl);
  CheckBytes('AS read D100 x2', pkg, [$00,$00,$00,$00,$00,$06,$01,$03,$00,$64,$00,$02]);

  //wire 反查
  Check('AS wire dev fc3@100 = D', drv.WireDev(3,100) = 8);
  Check('AS wire dev fc3@49200 = SR', drv.WireDev(3,49200) = 11);
  Check('AS wire dev fc3@65024 = E',  drv.WireDev(3,65024) = 13);
  Check('AS wire dev fc1@16384 = SM', drv.WireDev(1,16384) = 6);
  Check('AS wire dev fc1@64512 = HC', drv.WireDev(1,64512) = 7);

  drv.Free;

  writeln;
  writeln('total: ', pass+fail, '  pass: ', pass, '  fail: ', fail);
  if fail > 0 then
    halt(1);
end.
