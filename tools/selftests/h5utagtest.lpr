program h5utagtest;
{ 自测汇川 H5U 标签通讯驱动：设备表/地址、两种帧格式编解码、异常与残帧处理。 }
{$mode objfpc}{$H+}
uses SysUtils, Classes, commtypes, ProtocolTypes, Tag, PLCTagNumber,
     H5UTagDriver, H5UTagTCP;

type
  TTestDriver = class(TH5UTagTCPDriver)
  public
    function Enc(TagObj:TTagRec; ToWrite:TArrayOfDouble; var ResultLen:LongInt):BYTES;
    function Dec(pkg:TIOPacket; out values:TArrayOfDouble):TProtocolIOResult;
    function Addr(dev, address:LongInt):LongInt;
    function DevOf(func:LongInt):LongInt;
    function RemRead(buffer:BYTES):LongInt;
    function RemWrite(buffer:BYTES):LongInt;
  end;

var
  pass, fail:LongInt;

function TTestDriver.Enc(TagObj:TTagRec; ToWrite:TArrayOfDouble; var ResultLen:LongInt):BYTES;
begin
  Result := inherited EncodePkg(TagObj,ToWrite,ResultLen);
end;

function TTestDriver.Dec(pkg:TIOPacket; out values:TArrayOfDouble):TProtocolIOResult;
var
  tr:TTagRec;
begin
  tr := Default(TTagRec);
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

function TTestDriver.RemRead(buffer:BYTES):LongInt;
var
  tr:TTagRec;
begin
  tr := Default(TTagRec);
  Result := inherited RemainingBytesRead(buffer,tr);
end;

function TTestDriver.RemWrite(buffer:BYTES):LongInt;
begin
  Result := inherited RemainingBytesWrite(buffer);
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
  buf:BYTES;
  tn:TPLCTagNumber;
  ptt:TProtocolTagType;
begin
  pass := 0;
  fail := 0;

  //===================== 设备表 =====================
  writeln('--- device table ---');
  drv := TTestDriver.Create(nil);
  Check('UB func index 0', drv.DevOf(H5UTAG_FUNC_UB) = 0);
  Check('UW func index 1', drv.DevOf(H5UTAG_FUNC_UW) = 1);
  Check('unknown func -> -1', drv.DevOf(3) = -1);
  Check('UB is bit device', H5UTAG_DEV_ISBIT[0]);
  Check('UW is word device', not H5UTAG_DEV_ISBIT[1]);

  //===================== 地址 =====================
  writeln('--- address ---');
  Check('UB 21004E0 kept as is', drv.Addr(0,$21004E0) = $21004E0);
  Check('UW 21004F0 in bits (default)', drv.Addr(1,$21004F0) = $21004F0);
  drv.WordAddressInBits := false;
  Check('UW 21004F0 -> word 21004F', drv.Addr(1,$21004F0) = $21004F);
  drv.WordAddressInBits := true;

  //===================== MBAP 扩展格式：读 =====================
  writeln('--- hffMbapExt read ---');
  i := MakeTR(1, H5UTAG_FUNC_UB, $21004E0, 3);
  pkg := drv.Enc(i,nil,rl);
  CheckBytes('read UB 21004E0 x3',
    pkg, [$00,$00,$00,$00,$00,$08,$01,$01,$02,$10,$04,$E0,$00,$03]);
  Check('read bits expected answer len 10', rl = 10);

  i := MakeTR(1, H5UTAG_FUNC_UW, $21004F0, 2);
  pkg := drv.Enc(i,nil,rl);
  CheckBytes('read UW 21004F0 x2 (float)',
    pkg, [$00,$01,$00,$00,$00,$08,$01,$03,$02,$10,$04,$F0,$00,$02]);
  Check('read words expected answer len 13', rl = 13);

  p := RespPkg(pkg, [$00,$01,$00,$00,$00,$07,$01,$03,$04,$12,$34,$56,$78]);
  ior := drv.Dec(p,vals);
  Check('read words ioOk', ior = ioOk);
  Check('read words 2 values', Length(vals) = 2);
  Check('read words value 1 = 1234', vals[0] = $1234);
  Check('read words value 2 = 5678', vals[1] = $5678);

  //===================== MBAP 扩展格式：写 =====================
  writeln('--- hffMbapExt write ---');
  i := MakeTR(1, H5UTAG_FUNC_UB, $21004E1, 1);
  pkg := drv.Enc(i,[1],rl);
  CheckBytes('write single bit 1',
    pkg, [$00,$02,$00,$00,$00,$08,$01,$05,$02,$10,$04,$E1,$FF,$00]);
  Check('write bit expected answer len 8', rl = 8);

  pkg := drv.Enc(i,[0],rl);
  Check('write single bit 0 -> 0000', (pkg[12] = $00) and (pkg[13] = $00));

  SetLength(vals,2);
  vals[0] := $1234; vals[1] := $5678;
  i := MakeTR(1, H5UTAG_FUNC_UW, $2100510, 2);
  pkg := drv.Enc(i,vals,rl);
  CheckBytes('write UW 2100510 x2',
    pkg, [$00,$04,$00,$00,$00,$0D,$01,$10,$02,$10,$05,$10,$00,$02,$04,$12,$34,$56,$78]);

  //===================== HZ 格式 =====================
  writeln('--- hffHzExt ---');
  drv.FrameFormat := hffHzExt;
  i := MakeTR(1, H5UTAG_FUNC_UB, $21004E0, 3);
  pkg := drv.Enc(i,nil,rl);
  CheckBytes('HZ read UB 21004E0 x3',
    pkg, [$48,$5A,$00,$05,$00,$00,$00,$00,$00,$07,$01,$02,$10,$04,$E0,$00,$03]);
  Check('HZ read bits expected answer len 13', rl = 13);

  //HZ 应答：48 5A seq reserved len fc bytecount data
  p := RespPkg(pkg, [$48,$5A,$00,$04,$00,$00,$00,$00,$00,$04,$01,$01,$05]);
  ior := drv.Dec(p,vals);
  Check('HZ read bits ioOk', ior = ioOk);
  Check('HZ read bits 3 values', Length(vals) = 3);
  Check('HZ bit 0 = 1', vals[0] = 1);
  Check('HZ bit 1 = 0', vals[1] = 0);
  Check('HZ bit 2 = 1', vals[2] = 1);

  i := MakeTR(1, H5UTAG_FUNC_UW, $21004F0, 2);
  pkg := drv.Enc(i,nil,rl);
  CheckBytes('HZ read UW 21004F0 x2',
    pkg, [$48,$5A,$00,$06,$00,$00,$00,$00,$00,$07,$03,$02,$10,$04,$F0,$00,$02]);
  p := RespPkg(pkg, [$48,$5A,$00,$05,$00,$00,$00,$00,$00,$06,$03,$04,$41,$48,$00,$00]);
  ior := drv.Dec(p,vals);
  Check('HZ read words ioOk', ior = ioOk);
  Check('HZ read words 2 values', Length(vals) = 2);
  Check('HZ word 1 = 4148', vals[0] = $4148);

  drv.FrameFormat := hffMbapExt;

  //===================== 应答校验 =====================
  writeln('--- answer validation ---');
  i := MakeTR(1, H5UTAG_FUNC_UW, $21004F0, 2);
  pkg := drv.Enc(i,nil,rl);
  p := RespPkg(pkg, [$00,$06,$00,$00,$00,$03,$01,$83,$02]);
  ior := drv.Dec(p,vals);
  Check('exception 02 -> illegal address', ior = ioIllegalRegAddress);

  p := RespPkg(pkg, [$00,$07,$00,$00,$00,$03,$01,$83,$04]);
  ior := drv.Dec(p,vals);
  Check('exception 04 -> PLC error', ior = ioPLCError);

  p := RespPkg(pkg, [$00,$08,$00,$00,$00,$05,$01,$03,$04,$12,$34]);
  ior := drv.Dec(p,vals);
  Check('half frame -> comm error', ior = ioCommError);

  p := RespPkg(pkg, [$00,$09,$00,$00,$00,$07,$01,$02,$04,$12,$34,$56,$78]);
  ior := drv.Dec(p,vals);
  Check('wrong function -> comm error', ior = ioCommError);

  p := RespPkg(pkg, []);
  ior := drv.Dec(p,vals);
  Check('empty answer -> comm error', ior = ioCommError);

  //===================== 剩余字节 =====================
  writeln('--- remaining bytes ---');
  buf := [$00,$0A,$00,$00,$00,$07,$01,$03];
  Check('MBAP remaining 5 (total 13)', drv.RemRead(buf) = 5);
  drv.FrameFormat := hffHzExt;
  buf := [$48,$5A,$00,$0B,$00,$00,$00,$00,$00,$06,$03];
  Check('HZ remaining 5 (total 16)', drv.RemRead(buf) = 5);
  Check('HZ write remaining', drv.RemWrite(buf) = 5);
  drv.FrameFormat := hffMbapExt;

  //===================== 标签尺寸与地址字面量 =====================
  writeln('--- size and literal address ---');
  tn := TPLCTagNumber.Create(nil);
  try
    tn.MemReadFunction := H5UTAG_FUNC_UB;
    tn.MemWriteFunction := H5UTAG_FUNC_UB;
    tn.MemAddress := $21004E0;
    Check('UB size = 1 bit', drv.SizeOfTag(tn,false,ptt) = 1);
    Check('UB tag type = ptBit', ptt = ptBit);
    Check('UB literal = "UB 21004E0"', drv.LiteralTagAddress(tn) = 'UB 21004E0');

    tn.MemReadFunction := H5UTAG_FUNC_UW;
    tn.MemWriteFunction := H5UTAG_FUNC_UW;
    tn.MemAddress := $21004F0;
    Check('UW size = 16 bits', drv.SizeOfTag(tn,false,ptt) = 16);
    Check('UW tag type = ptWord', ptt = ptWord);
    Check('UW literal = "UW 21004F0"', drv.LiteralTagAddress(tn) = 'UW 21004F0');
  finally
    tn.Destroy;
  end;

  drv.Destroy;

  writeln;
  writeln('PASS: ',pass,'   FAIL: ',fail,'   TOTAL: ',pass+fail);
  if fail > 0 then
    Halt(1);
end.
