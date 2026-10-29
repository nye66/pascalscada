program svgcliptest;

{$mode objfpc}{$H+}

// Reproduz os tres modos de desenho do THMIFlowVectorControl sobre um canvas
// nao quadrado, para achar onde o desenho esta' sendo cortado.
// Reproduces the three drawing modes of THMIFlowVectorControl on a non-square
// canvas, to find where the drawing gets cut.

uses
  SysUtils, Classes, BGRABitmap, BGRABitmapTypes, BGRACanvas2D,
  BGRASVG, BGRASVGType, BGRASVGShapes;

var
  svg: TBGRASVG;
  bmp: TBGRABitmap;
  c2d: TBGRACanvas2D;

procedure Render(const aFile: string; w, h: Integer; modo: Integer);
begin
  bmp := TBGRABitmap.Create(w, h, BGRAWhite);
  c2d := TBGRACanvas2D.Create(bmp);
  try
    case modo of
      //Stretch=True, Proportional=True
      1: svg.StretchDraw(c2d, taLeftJustify, tlTop, 0, 0, w - 1, h - 1);
      //Stretch=True, Proportional=False
      2: svg.StretchDraw(c2d, 0, 0, w - 1, h - 1);
      //Stretch=False
      3: svg.Draw(c2d, 0, 0, cuPixel);
      //natural size via StretchDraw com altura/largura computadas
      4: svg.StretchDraw(c2d, 0, 0, cuPixel);
    end;
  finally
    c2d.Free;
  end;
  bmp.SaveToFile(aFile);
  bmp.Free;
  writeln('saved ', aFile);
end;

begin
  if ParamCount < 1 then
  begin
    writeln('uso: svgcliptest <arquivo.svg>');
    halt(1);
  end;

  svg := TBGRASVG.Create;
  try
    svg.LoadFromFile(ParamStr(1));
    //controle mais largo que alto (200x150) e mais alto que largo (150x200)
    Render(ChangeFileExt(ParamStr(1), '') + '_m1_200x150.png', 200, 150, 1);
    Render(ChangeFileExt(ParamStr(1), '') + '_m2_200x150.png', 200, 150, 2);
    Render(ChangeFileExt(ParamStr(1), '') + '_m3_200x150.png', 200, 150, 3);
    Render(ChangeFileExt(ParamStr(1), '') + '_m1_150x200.png', 150, 200, 1);
    Render(ChangeFileExt(ParamStr(1), '') + '_m4_200x150.png', 200, 150, 4);
  finally
    svg.Free;
  end;
end.
