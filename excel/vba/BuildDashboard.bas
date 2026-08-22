Attribute VB_Name = "BuildDashboard"
Option Explicit

Public Sub BuildPortfolioPulseDashboard()
    On Error GoTo ErrHandler

    Dim ws As Worksheet
    Set ws = ThisWorkbook.Worksheets("Dashboard")

    Application.ScreenUpdating = False

    ws.Range("A1:J38").UnMerge
    ws.Range("A1:J38").ClearContents
    ws.Range("A1:J38").ClearFormats
    DeleteDashboardShapes ws

    ws.Cells.Font.Name = "Aptos"
    ws.Cells.Font.Size = 10
    ActiveWindow.DisplayGridlines = False

    ws.Columns("A").ColumnWidth = 3
    ws.Columns("B").ColumnWidth = 19
    ws.Columns("C").ColumnWidth = 4
    ws.Columns("D").ColumnWidth = 19
    ws.Columns("E").ColumnWidth = 4
    ws.Columns("F").ColumnWidth = 19
    ws.Columns("G").ColumnWidth = 4
    ws.Columns("H").ColumnWidth = 19
    ws.Columns("I").ColumnWidth = 4
    ws.Columns("J").ColumnWidth = 3

    With ws.Range("B2:I3")
        .Merge
        .Value = "PORTFOLIO PULSE"
        .Interior.Color = RGB(11, 31, 58)
        .Font.Color = RGB(255, 255, 255)
        .Font.Bold = True
        .Font.Size = 22
        .HorizontalAlignment = xlLeft
        .VerticalAlignment = xlCenter
    End With

    With ws.Range("B4:I4")
        .Merge
        .Value = "Interactive Multi-Asset Portfolio & Risk Analytics"
        .Font.Color = RGB(90, 90, 90)
        .Font.Size = 11
    End With

    AddMacroButton ws, "B6", "C7", "Check Allocations", "CheckAllocations"
    AddMacroButton ws, "D6", "E7", "Refresh Portfolio", "RefreshPortfolio"
    AddMacroButton ws, "F6", "I7", "Generate Report", "GeneratePortfolioReport"

    FormatSectionHeader ws.Range("B9:I9"), "PORTFOLIO OVERVIEW"

    MakeKPICard ws, "B11:C14", "Portfolio CAGR", "=Analytics!B4", "0.00%;[Red](0.00%);-"
    MakeKPICard ws, "D11:E14", "60/40 CAGR", "=Analytics!C4", "0.00%;[Red](0.00%);-"
    MakeKPICard ws, "F11:G14", "Sharpe Ratio", "=Analytics!B6", "0.00x"
    MakeKPICard ws, "H11:I14", "Max Drawdown", "=Analytics!B7", "0.00%;[Red](0.00%);-"

    MakeKPICard ws, "B16:C19", "Excess Ann. Return", "=Analytics!B9", "0.00%;[Red](0.00%);-"
    MakeKPICard ws, "D16:E19", "Beta vs 60/40", "=Analytics!B8", "0.00x"
    MakeKPICard ws, "F16:G19", "Ending Value", "=Analytics!B16", "$#,##0;[Red]($#,##0);-"
    MakeKPICard ws, "H16:I19", "Benchmark Value", "=Analytics!B17", "$#,##0;[Red]($#,##0);-"

    FormatSectionHeader ws.Range("B21:E21"), "CURRENT ALLOCATION"

    ws.Range("B22").Value = "Asset"
    ws.Range("C22").Value = "Weight"
    ws.Range("B23").Value = "VTI": ws.Range("C23").Formula = "=Portfolio!C9"
    ws.Range("B24").Value = "VXUS": ws.Range("C24").Formula = "=Portfolio!C10"
    ws.Range("B25").Value = "AGG": ws.Range("C25").Formula = "=Portfolio!C11"
    ws.Range("B26").Value = "SGOV": ws.Range("C26").Formula = "=Portfolio!C12"
    ws.Range("B22:C22").Font.Bold = True
    ws.Range("C23:C26").NumberFormat = "0.0%"
    ws.Range("B22:C26").Borders.LineStyle = xlContinuous
    ws.Range("B22:C26").Borders.Color = RGB(220, 220, 220)

    FormatSectionHeader ws.Range("F21:I21"), "HISTORICAL STRESS TESTS"
    ws.Range("F22").Value = "Scenario"
    ws.Range("G22").Value = "Return"
    ws.Range("H22").Value = "Max DD"
    ws.Range("I22").Value = "Recovery"

    ws.Range("F23").Value = "GFC"
    ws.Range("G23").Formula = "='Stress Tests'!D4"
    ws.Range("H23").Formula = "='Stress Tests'!E4"
    ws.Range("I23").Formula = "='Stress Tests'!F4"

    ws.Range("F24").Value = "COVID"
    ws.Range("G24").Formula = "='Stress Tests'!D5"
    ws.Range("H24").Formula = "='Stress Tests'!E5"
    ws.Range("I24").Formula = "='Stress Tests'!F5"

    ws.Range("F25").Value = "2022 Rates"
    ws.Range("G25").Formula = "='Stress Tests'!D6"
    ws.Range("H25").Formula = "='Stress Tests'!E6"
    ws.Range("I25").Formula = "='Stress Tests'!F6"

    ws.Range("F22:I22").Font.Bold = True
    ws.Range("G23:H25").NumberFormat = "0.0%;[Red](0.0%);-"
    ws.Range("F22:I25").Borders.LineStyle = xlContinuous
    ws.Range("F22:I25").Borders.Color = RGB(220, 220, 220)

    FormatSectionHeader ws.Range("B28:I28"), "MODEL AUDIT & METHODOLOGY"

    ws.Range("B29").Value = "Analysis Start": ws.Range("C29").Formula = "=Analytics!B11"
    ws.Range("B30").Value = "Analysis End": ws.Range("C30").Formula = "=Analytics!B12"
    ws.Range("B31").Value = "Last Refresh": ws.Range("C31").Formula = "=Analytics!B13"
    ws.Range("B32").Value = "Weights Used": ws.Range("C32").Formula = "=Analytics!B14"

    ws.Range("B29:B32").Font.Bold = True
    ws.Range("C29:C30").NumberFormat = "yyyy-mm-dd"
    ws.Range("C31").NumberFormat = "yyyy-mm-dd hh:mm"

    With ws.Range("B34:I35")
        .Merge
        .Value = "Educational analysis only. Historical performance and stress scenarios do not predict future results."
        .Font.Italic = True
        .Font.Color = RGB(100, 100, 100)
        .WrapText = True
    End With

    ws.Activate
    ws.Range("B2").Select

    Application.ScreenUpdating = True
    MsgBox "Portfolio Pulse dashboard rebuilt successfully.", vbInformation, "Portfolio Pulse"
    Exit Sub

ErrHandler:
    Application.ScreenUpdating = True
    MsgBox "Dashboard build failed: " & Err.Description, vbCritical, "Portfolio Pulse"
End Sub

Private Sub FormatSectionHeader(ByVal target As Range, ByVal titleText As String)
    With target
        .Merge
        .Value = titleText
        .Interior.Color = RGB(11, 31, 58)
        .Font.Color = RGB(255, 255, 255)
        .Font.Bold = True
        .HorizontalAlignment = xlLeft
        .VerticalAlignment = xlCenter
    End With
End Sub

Private Sub MakeKPICard(ByVal ws As Worksheet, ByVal cardRange As String, _
                        ByVal labelText As String, ByVal formulaText As String, _
                        ByVal numberFmt As String)
    Dim r As Range
    Dim labelR As Range
    Dim valueR As Range

    Set r = ws.Range(cardRange)
    r.Interior.Color = RGB(245, 247, 250)
    r.Borders.LineStyle = xlContinuous
    r.Borders.Color = RGB(220, 225, 230)

    Set labelR = r.Rows(1)
    labelR.Merge
    labelR.Value = labelText
    labelR.Font.Bold = True
    labelR.Font.Color = RGB(90, 90, 90)
    labelR.HorizontalAlignment = xlCenter

    Set valueR = r.Offset(1, 0).Resize(r.Rows.Count - 1, r.Columns.Count)
    valueR.Merge
    valueR.Formula = formulaText
    valueR.NumberFormat = numberFmt
    valueR.Font.Bold = True
    valueR.Font.Size = 18
    valueR.HorizontalAlignment = xlCenter
    valueR.VerticalAlignment = xlCenter
End Sub

Private Sub AddMacroButton(ByVal ws As Worksheet, ByVal topLeft As String, _
                           ByVal bottomRight As String, ByVal caption As String, _
                           ByVal macroName As String)
    Dim target As Range
    Dim shp As Shape

    Set target = ws.Range(topLeft & ":" & bottomRight)
    Set shp = ws.Shapes.AddShape(msoShapeRoundedRectangle, _
                                 target.Left, target.Top, _
                                 target.Width, target.Height)

    With shp
        .Name = "btn_" & Replace(caption, " ", "_")
        .TextFrame2.TextRange.Characters.Text = caption
        .TextFrame2.TextRange.Font.Bold = msoTrue
        .TextFrame2.TextRange.Font.Size = 11
        .TextFrame2.TextRange.Font.Fill.ForeColor.RGB = RGB(255, 255, 255)
        .Fill.ForeColor.RGB = RGB(31, 78, 121)
        .Line.Visible = msoFalse
        .OnAction = "'" & ThisWorkbook.Name & "'!" & macroName
    End With
End Sub

Private Sub DeleteDashboardShapes(ByVal ws As Worksheet)
    Dim i As Long
    For i = ws.Shapes.Count To 1 Step -1
        ws.Shapes(i).Delete
    Next i
End Sub
