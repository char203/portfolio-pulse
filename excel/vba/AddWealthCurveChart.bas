Attribute VB_Name = "AddWealthCurveChart"
Option Explicit

Public Sub AddWealthCurveChart()
    On Error GoTo ErrHandler

    Dim dashboard As Worksheet
    Dim dataWS As Worksheet
    Dim chartObj As ChartObject
    Dim lastRow As Long
    Dim chartName As String

    If Not WorksheetExists("Dashboard") Then
        MsgBox "Dashboard sheet not found.", vbCritical, "Portfolio Pulse"
        Exit Sub
    End If

    If Not WorksheetExists("Wealth Curve Data") Then
        MsgBox "Wealth Curve Data sheet not found." & vbCrLf & vbCrLf & _
               "Run Refresh Portfolio first using the latest excel_bidirectional.py.", _
               vbExclamation, "Portfolio Pulse"
        Exit Sub
    End If

    Set dashboard = ThisWorkbook.Worksheets("Dashboard")
    Set dataWS = ThisWorkbook.Worksheets("Wealth Curve Data")

    chartName = "PortfolioWealthCurve"

    lastRow = dataWS.Cells(dataWS.Rows.Count, "A").End(xlUp).Row

    If lastRow < 3 Then
        MsgBox "Not enough wealth-curve data to create the chart.", _
               vbExclamation, "Portfolio Pulse"
        Exit Sub
    End If

    ' Remove the prior chart if one already exists.
    On Error Resume Next
    dashboard.ChartObjects(chartName).Delete
    On Error GoTo ErrHandler

    Set chartObj = dashboard.ChartObjects.Add( _
        Left:=dashboard.Range("B37").Left, _
        Top:=dashboard.Range("B37").Top, _
        Width:=dashboard.Range("B37:I37").Width, _
        Height:=320 _
    )

    chartObj.Name = chartName

    With chartObj.Chart
        .ChartType = xlLine
        .HasTitle = True
        .ChartTitle.Text = "$10,000 Growth: Portfolio Pulse vs. 60/40"

        .SeriesCollection.NewSeries
        With .SeriesCollection(1)
            .Name = "Portfolio Pulse"
            .XValues = dataWS.Range("A2:A" & lastRow)
            .Values = dataWS.Range("B2:B" & lastRow)
        End With

        .SeriesCollection.NewSeries
        With .SeriesCollection(2)
            .Name = "60/40 Benchmark"
            .XValues = dataWS.Range("A2:A" & lastRow)
            .Values = dataWS.Range("C2:C" & lastRow)
        End With

        .HasLegend = True
        .Legend.Position = xlLegendPositionBottom
        .DisplayBlanksAs = xlNotPlotted

        On Error Resume Next
        .Axes(xlValue).TickLabels.NumberFormat = "$#,##0"
        .Axes(xlCategory).TickLabels.NumberFormat = "mmm-yy"
        On Error GoTo ErrHandler
    End With

    ' Interpretation strip below chart
    dashboard.Range("B55:I56").UnMerge
    With dashboard.Range("B55:I56")
        .Merge
        .Formula = _
            "=""Ending value: Portfolio Pulse "" & TEXT(Analytics!B16,""$#,##0"") & " & _
            """ vs. 60/40 "" & TEXT(Analytics!B17,""$#,##0"") & " & _
            """ | Difference: "" & TEXT(Analytics!B16-Analytics!B17,""$#,##0"")"
        .Font.Italic = True
        .Font.Color = RGB(90, 90, 90)
        .HorizontalAlignment = xlLeft
        .VerticalAlignment = xlCenter
        .WrapText = True
    End With

    MsgBox "Wealth curve added to the Dashboard successfully.", _
           vbInformation, "Portfolio Pulse"
    Exit Sub

ErrHandler:
    MsgBox "Could not create wealth curve: " & Err.Description, _
           vbCritical, "Portfolio Pulse"
End Sub

Private Function WorksheetExists(ByVal sheetName As String) As Boolean
    Dim ws As Worksheet

    On Error Resume Next
    Set ws = ThisWorkbook.Worksheets(sheetName)
    WorksheetExists = Not ws Is Nothing
    On Error GoTo 0
End Function
