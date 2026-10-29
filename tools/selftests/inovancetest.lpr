program inovancetest;
{ 自测汇川驱动：AM/H3U/H5U 地址映射 + Modbus TCP 帧编解码 + 事务ID反查。 }
{$mode objfpc}{$H+}
uses SysUtils, Classes, commtypes, ProtocolTypes, Tag, InovanceDriver, InovanceTCP;

type
  TTestDriver = class(TInovanceTCPDriver)
  public
    function Enc(TagObj:TTagRec; ToWrite:TArrayOfDouble; var ResultLen:LongInt):BYTES;
    function Dec(pkg:TIOPacket; out values:TArrayOfDouble):TProtocolIOResult;
    function Addr(dev, address:LongInt):LongInt;
    function DevOf(func:LongInt):LongInt;
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

function TTestDriver.DevOf(func:LongInt):LongInt;
begin
  Result := inherited DeviceIndex(func);
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

  //===================== H5U 系列 =====================
  writeln('--- H5U series address map ---');
  drv := TTestDriver.Create(nil);
  Check('default series is H5U', drv.Series = ivsH5U);

  Check('H5U D100 -> 100',   drv.Addr(drv.DevOf(INOVANCE_FUNC_D),100) = 100);
  Check('H5U M100 -> 100',   drv.Addr(drv.DevOf(INOVANCE_FUNC_M),100) = 100);
  Check('H5U X10(oct)->63496', drv.Addr(drv.DevOf(INOVANCE_FUNC_X),10) = 8+63488);
  Check('H5U X17(oct)->63503', drv.Addr(drv.DevOf(INOVANCE_FUNC_X),17) = 15+63488);
  Check('H5U Y7 -> 64519',   drv.Addr(drv.DevOf(INOVANCE_FUNC_Y),7) = 7+64512);
  Check('H5U S50 -> 57394',  drv.Addr(drv.DevOf(INOVANCE_FUNC_S),50) = 50+57344);
  Check('H5U B100 -> 12388', drv.Addr(drv.DevOf(INOVANCE_FUNC_B),100) = 100+12288);
  Check('H5U R100 -> 12388', drv.Addr(drv.DevOf(INOVANCE_FUNC_R),100) = 100+12288);
  Check('H5U no Q', not drv.DeviceSupportedBySeries(drv.DevOf(INOVANCE_FUNC_Q)));
  Check('H5U no MW', not drv.DeviceSupportedBySeries(drv.DevOf(INOVANCE_FUNC_MW)));
  Check('H5U no T', not drv.DeviceSupportedBySeries(drv.DevOf(INOVANCE_FUNC_T)));

  //H5U 读 D100 2 个字
  i := MakeTR(1, INOVANCE_FUNC_D, 100, 2);
  pkg := drv.Enc(i,nil,rl);
  CheckBytes('H5U read D100 x2', pkg, [$00,$00,$00,$00,$00,$06,$01,$03,$00,$64,$00,$02]);
  Check('expected answer len 13', rl = 13);

  //应答解析（事务 ID 0000 反查 D）
  p := RespPkg(pkg, [$00,$00,$00,$00,$00,$07,$01,$03,$04,$12,$34,$00,$56]);
  ior := drv.Dec(p,vals);
  Check('H5U read ioOk', ior = ioOk);
  Check('H5U read 2 values', Length(vals) = 2);
  Check('H5U value0 = 4660', Trunc(vals[0]) = $1234);
  Check('H5U value1 = 86',   Trunc(vals[1]) = $0056);

  //读 X（fc02，八进制 X10 → 63496 = F028）
  i := MakeTR(1, INOVANCE_FUNC_X, 10, 8);
  drv.Norm(i);
  pkg := drv.Enc(i,nil,rl);
  CheckBytes('H5U read X10 x8 fc02', pkg, [$00,$01,$00,$00,$00,$06,$01,$02,$F8,$08,$00,$08]);

  //写单个位 M100=1 (fc05)
  SetLength(vals,1); vals[0] := 1;
  i := MakeTR(1, INOVANCE_FUNC_M, 100, 1);
  pkg := drv.Enc(i,vals,rl);
  CheckBytes('H5U write M100=1 fc05', pkg, [$00,$02,$00,$00,$00,$06,$01,$05,$00,$64,$FF,$00]);

  //写单个字 D100=1234 (fc06)
  SetLength(vals,1); vals[0] := 1234;
  i := MakeTR(1, INOVANCE_FUNC_D, 100, 1);
  pkg := drv.Enc(i,vals,rl);
  CheckBytes('H5U write D100=1234 fc06', pkg, [$00,$03,$00,$00,$00,$06,$01,$06,$00,$64,$04,$D2]);
  p := RespPkg(pkg, [$00,$03,$00,$00,$00,$06,$01,$06,$00,$64,$04,$D2]);
  ior := drv.Dec(p,vals);
  Check('H5U write reg ioOk', ior = ioOk);
  Check('H5U write reg echo 1234', Trunc(vals[0]) = 1234);

  //多写字 D0..1 = [1000, 2000] (fc10)
  SetLength(vals,2); vals[0]:=1000; vals[1]:=2000;
  i := MakeTR(1, INOVANCE_FUNC_D, 0, 2);
  pkg := drv.Enc(i,vals,rl);
  CheckBytes('H5U write D0..1 fc10', pkg, [$00,$04,$00,$00,$00,$0B,$01,$10,$00,$00,$00,$02,$04,$03,$E8,$07,$D0]);

  //X 不可写
  SetLength(vals,1); vals[0] := 1;
  i := MakeTR(1, INOVANCE_FUNC_X, 0, 1);
  pkg := drv.Enc(i,vals,rl);
  Check('H5U write X rejected (nil)', pkg = nil);

  drv.Free;

  //===================== H3U 系列 =====================
  writeln('--- H3U series address map ---');
  drv := TTestDriver.Create(nil);
  drv.Series := ivsH3U;

  Check('H3U D100 -> 100',    drv.Addr(drv.DevOf(INOVANCE_FUNC_D),100) = 100);
  Check('H3U M100 -> 100',    drv.Addr(drv.DevOf(INOVANCE_FUNC_M),100) = 100);
  Check('H3U X17 -> 63503',   drv.Addr(drv.DevOf(INOVANCE_FUNC_X),17) = 15+63488);
  Check('H3U Y7 -> 64519',    drv.Addr(drv.DevOf(INOVANCE_FUNC_Y),7) = 7+64512);
  Check('H3U S50 -> 57394',   drv.Addr(drv.DevOf(INOVANCE_FUNC_S),50) = 50+57344);
  Check('H3U SD10 -> 9226',   drv.Addr(drv.DevOf(INOVANCE_FUNC_SD),10) = 10+9216);
  Check('H3U R100 -> 12388',  drv.Addr(drv.DevOf(INOVANCE_FUNC_R),100) = 100+12288);
  Check('H3U T10 -> 61450',   drv.Addr(drv.DevOf(INOVANCE_FUNC_T),10) = 10+61440);
  Check('H3U C50 -> 62514',   drv.Addr(drv.DevOf(INOVANCE_FUNC_C),50) = 50+62464);
  Check('H3U C250 -> 63232',  drv.Addr(drv.DevOf(INOVANCE_FUNC_C),250) = (250-200)*2+63232);
  Check('H3U C199 -> 62663',  drv.Addr(drv.DevOf(INOVANCE_FUNC_C),199) = 199+62464);
  Check('H3U no Q', not drv.DeviceSupportedBySeries(drv.DevOf(INOVANCE_FUNC_Q)));
  Check('H3U no B', not drv.DeviceSupportedBySeries(drv.DevOf(INOVANCE_FUNC_B)));
  Check('H3U no MW', not drv.DeviceSupportedBySeries(drv.DevOf(INOVANCE_FUNC_MW)));

  //H3U C 字：C150..C199 一段（wire 62614 = F476），C200 起映射到另一段
  i := MakeTR(1, INOVANCE_FUNC_C, 150, 50);
  drv.Norm(i);
  Check('C150 normalized wire = 62614', i.Address = 62614);
  pkg := drv.Enc(i,nil,rl);
  CheckBytes('H3U read C150 x50 fc03', pkg, [$00,$00,$00,$00,$00,$06,$01,$03,$F4,$96,$00,$32]);

  drv.Free;

  //===================== AM 系列 =====================
  writeln('--- AM series address map ---');
  drv := TTestDriver.Create(nil);
  drv.Series := ivsAM;

  Check('AM M100 -> 100',   drv.Addr(drv.DevOf(INOVANCE_FUNC_M),100) = 100);
  Check('AM Q83 -> 83',     drv.Addr(drv.DevOf(INOVANCE_FUNC_Q),83) = 83);
  Check('AM I83 -> 83',     drv.Addr(drv.DevOf(INOVANCE_FUNC_I),83) = 83);
  Check('AM MW100 -> 100',  drv.Addr(drv.DevOf(INOVANCE_FUNC_MW),100) = 100);
  Check('AM MD50 -> 100',   drv.Addr(drv.DevOf(INOVANCE_FUNC_MD),50) = 100);
  Check('AM no D', not drv.DeviceSupportedBySeries(drv.DevOf(INOVANCE_FUNC_D)));
  Check('AM no X', not drv.DeviceSupportedBySeries(drv.DevOf(INOVANCE_FUNC_X)));

  //AM 读 MW100 2 个字（fc03）
  i := MakeTR(1, INOVANCE_FUNC_MW, 100, 2);
  pkg := drv.Enc(i,nil,rl);
  CheckBytes('AM read MW100 x2', pkg, [$00,$00,$00,$00,$00,$06,$01,$03,$00,$64,$00,$02]);

  //AM 读 Q 位（fc01）
  i := MakeTR(1, INOVANCE_FUNC_Q, 83, 10);
  pkg := drv.Enc(i,nil,rl);
  CheckBytes('AM read Q83 x10 fc01', pkg, [$00,$01,$00,$00,$00,$06,$01,$01,$00,$53,$00,$0A]);

  //AM 读 I 位（fc02）
  i := MakeTR(1, INOVANCE_FUNC_I, 0, 8);
  pkg := drv.Enc(i,nil,rl);
  CheckBytes('AM read I0 x8 fc02', pkg, [$00,$02,$00,$00,$00,$06,$01,$02,$00,$00,$00,$08]);

  //AM 读 MD50 2 个字（MD50 = 双字，占 2 寄存器 100..101）
  i := MakeTR(1, INOVANCE_FUNC_MD, 50, 2);
  drv.Norm(i);
  pkg := drv.Enc(i,nil,rl);
  CheckBytes('AM read MD50 x2', pkg, [$00,$03,$00,$00,$00,$06,$01,$03,$00,$64,$00,$02]);

  //AM Q 与 M 同 wire 地址：事务 ID 反查（连续两次编码，各自事务 ID 不同）
  i := MakeTR(1, INOVANCE_FUNC_M, 10, 1);
  pkg := drv.Enc(i,nil,rl);
  CheckBytes('AM read M10 (tx 0004)', pkg, [$00,$04,$00,$00,$00,$06,$01,$01,$00,$0A,$00,$01]);
  p := RespPkg(pkg, [$00,$04,$00,$00,$00,$04,$01,$01,$01,$01]);
  ior := drv.Dec(p,vals);
  Check('AM M read ioOk', ior = ioOk);
  Check('AM M10 value = 1', Trunc(vals[0]) = 1);

  //AM 写 MW100=1000 (fc06)
  SetLength(vals,1); vals[0] := 1000;
  i := MakeTR(1, INOVANCE_FUNC_MW, 100, 1);
  pkg := drv.Enc(i,vals,rl);
  CheckBytes('AM write MW100=1000 fc06', pkg, [$00,$05,$00,$00,$00,$06,$01,$06,$00,$64,$03,$E8]);

  drv.Free;

  writeln;
  writeln('total: ', pass+fail, '  pass: ', pass, '  fail: ', fail);
  if fail > 0 then
    halt(1);
end.
