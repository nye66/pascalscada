program lrscheck;
{ 验证 xinjeicon.lrs 语法有效且资源可被 LazarusResources 找到 }
{$mode objfpc}{$H+}
uses SysUtils, Classes, LResources, Graphics, IntfGraphics, GraphType;

var
  r: TLResource;
  bmp: TCustomBitmap;

  procedure CheckRes(const AName: string);
  begin
    r := LazarusResources.Find(AName);
    if r = nil then
    begin
      writeln('FAIL: resource not found: ', AName);
      halt(1);
    end;
    writeln('OK: type=', r.ValueType, ' len=', Length(r.Value));
    bmp := CreateBitmapFromLazarusResource(r);
    if bmp = nil then
    begin
      writeln('FAIL: bitmap decode returned nil: ', AName);
      halt(1);
    end;
    try
      writeln('OK: decoded ', bmp.ClassName, ' ', bmp.Width, 'x', bmp.Height);
    finally
      bmp.Free;
    end;
  end;

begin
{$I xinjeicon.lrs}
  CheckRes('TXinJETCPDriver');
  CheckRes('TLGXDriver');
  CheckRes('TS7CommPlusDriver');
  CheckRes('TDeltaTCPDriver');
  CheckRes('TInovanceTCPDriver');
  CheckRes('TH5UTagTCPDriver');
end.
