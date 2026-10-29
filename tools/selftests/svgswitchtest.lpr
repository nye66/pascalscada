program svgswitchtest;

{$mode objfpc}{$H+}

// Renderiza o SVG de duas posicoes nos dois estados, para conferir que o
// display:none/visible funciona no BGRASVG de verdade.
// Renders the two position SVG in both states, to check that display:none /
// visible really works in BGRASVG.

uses
  SysUtils, Classes, BGRABitmap, BGRABitmapTypes, BGRACanvas2D,
  BGRASVG, BGRASVGType, BGRASVGShapes;

var
  svg: TBGRASVG;
  bmp: TBGRABitmap;
  c2d: TBGRACanvas2D;

function FindEl(const aContent: TSVGContent; const aId: string): TSVGElement;
var
  i: Integer;
begin
  Result := nil;
  if aContent = nil then exit;
  for i := 0 to aContent.ElementCount - 1 do
  begin
    if not aContent.IsSVGElement[i] then continue;
    if aContent.Element[i].HasAttribute('id') and
       (LowerCase(aContent.Element[i].Attribute['id']) = aId) then
    begin
      Result := aContent.Element[i];
      exit;
    end;
    //os filhos de um grupo/gradiente ficam no Content dele
    //the children of a group/gradient live in its own Content
    if aContent.Element[i] is TSVGGroup then
    begin
      Result := FindEl(TSVGGroup(aContent.Element[i]).Content, aId);
      if Assigned(Result) then exit;
    end;
    if aContent.Element[i] is TSVGDefine then
    begin
      Result := FindEl(TSVGDefine(aContent.Element[i]).Content, aId);
      if Assigned(Result) then exit;
    end;
  end;
end;

procedure Render(const aFile: string);
const
  S = 4;   // escala: 112.5 x 109.23 -> 450 x 437
var
  w, h: Integer;
begin
  //o viewBox e' 112.5 x 109.23; a escala 4 da' 450 x 437
  //the viewBox is 112.5 x 109.23; scale 4 gives 450 x 437
  w := round(112.5 * S);
  h := round(109.23 * S);
  bmp := TBGRABitmap.Create(w, h, BGRAWhite);
  c2d := TBGRACanvas2D.Create(bmp);
  try
    c2d.scale(S, S);
    svg.Draw(c2d, 0, 0);
  finally
    c2d.Free;
  end;
  bmp.SaveToFile(aFile);
  bmp.Free;
  writeln('saved ', aFile, ' ', w, 'x', h);
end;

var
  elL, elR: TSVGElement;
begin
  if ParamCount < 1 then
  begin
    writeln('uso: svgswitchtest <arquivo.svg> [saida]');
    halt(1);
  end;

  svg := TBGRASVG.Create;
  try
    svg.LoadFromFile(ParamStr(1));
    writeln('elementos: ', svg.Content.ElementCount);

    elL := FindEl(svg.Content, 'handle_left');
    elR := FindEl(svg.Content, 'handle_right');
    writeln('Handle_Left  achado: ', Assigned(elL), ' visible: ', Assigned(elL) and elL.Visible);
    writeln('Handle_Right achado: ', Assigned(elR), ' visible: ', Assigned(elR) and elR.Visible);

    Render(ChangeFileExt(ParamStr(1), '') + '_estado1.png');

    if Assigned(elL) and Assigned(elR) then
    begin
      elL.Visible := False;
      elR.Visible := True;
      writeln('depois de trocar: left=', elL.Visible, ' right=', elR.Visible);
      Render(ChangeFileExt(ParamStr(1), '') + '_estado2.png');
    end;
  finally
    svg.Free;
  end;
end.
