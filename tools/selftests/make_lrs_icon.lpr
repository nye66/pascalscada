program make_lrs_icon;
{ 把 PNG 图标编码成 Lazarus .lrs 资源格式并追加到目标 .lrs 文件。
  用法: make_lrs_icon <图标.png> <组件类名> <目标.lrs>
  若目标文件里已有该类名的资源则跳过。 }
{$mode objfpc}{$H+}
uses SysUtils, Classes;

function EncodeBytes(const data: TBytes): string;
var
  b: byte;
  lit: string;
  i: integer;
begin
  Result := '';
  lit := '';
  for i := 0 to High(data) do
  begin
    b := data[i];
    if (b >= 32) and (b <= 126) and (b <> 39) then  { 39 = 单引号 }
      lit := lit + Chr(b)
    else
    begin
      if lit <> '' then
      begin
        Result := Result + '''' + StringReplace(lit, '''', '''''',
                   [rfReplaceAll]) + '''';
        lit := '';
      end;
      Result := Result + '#' + IntToStr(b);
    end;
  end;
  if lit <> '' then
    Result := Result + '''' + StringReplace(lit, '''', '''''', [rfReplaceAll]) + '''';
end;

procedure AppendWrapped(const fname, cls, tokens: string);
var
  fs: TFileStream;
  src: string;
  block, line, tok: string;
  pos_, j: integer;
  first: boolean;
  sl: TStringList;
begin
  sl := TStringList.Create;
  try
    if FileExists(fname) then
    begin
      sl.LoadFromFile(fname);
      src := sl.Text;
      if Pos('LazarusResources.Add(''' + cls + '''', src) > 0 then
      begin
        writeln('SKIP: ', cls, ' already present');
        exit;
      end;
      if (src <> '') and (src[Length(src)] <> #10) then
        src := src + #13#10;
    end
    else
      src := '';
    block := 'LazarusResources.Add(''' + cls + ''',''PNG'',[' + #13#10;
    line := '  ';
    first := True;
    pos_ := 1;
    while pos_ <= Length(tokens) do
    begin
      { 取一个完整 token: #NNN 或 'lit' }
      if tokens[pos_] = '#' then
      begin
        j := pos_;
        while (j <= Length(tokens)) and (tokens[j] in ['0'..'9']) do
          Inc(j);
      end
      else
      begin
        j := pos_ + 1;
        repeat
          while (j <= Length(tokens)) and (tokens[j] <> '''') do
            Inc(j);
          Inc(j);  { 越过结束引号 }
        until (j > Length(tokens)) or (tokens[j] <> '''');
      end;
      tok := Copy(tokens, pos_, j - pos_);
      if (Length(line) + Length(tok) > 78) and (line <> '  +') then
      begin
        if not first then
          block := block + #13#10;
        block := block + line;
        line := '  +';
        first := False;
      end;
      line := line + tok;
      pos_ := j;
    end;
    if line <> '  +' then
    begin
      if not first then
        block := block + #13#10;
      block := block + line;
    end;
    block := block + #13#10 + ']);' + #13#10;

    sl.Text := src + block;
    sl.SaveToFile(fname);
    writeln('APPENDED ', cls, ' -> ', fname);
  finally
    sl.Free;
  end;
end;

var
  png: TFileStream;
  data: TBytes;
begin
  if ParamCount < 3 then
  begin
    writeln('usage: make_lrs_icon <icon.png> <ClassName> <target.lrs>');
    halt(1);
  end;
  png := TFileStream.Create(ParamStr(1), fmOpenRead);
  try
    SetLength(data, png.Size);
    if png.Size > 0 then
      png.ReadBuffer(data[0], png.Size);
  finally
    png.Free;
  end;
  AppendWrapped(ParamStr(3), ParamStr(2), EncodeBytes(data));
end.
