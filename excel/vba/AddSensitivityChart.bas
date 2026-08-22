Attribute VB_Name = "AddSensitivityChart"
Option Explicit

Public Sub AddSensitivityChart()
    On Error GoTo ErrHandler

    Dim dash As Worksheet
    Dim sens As Worksheet
    Dim chartObj As ChartObject
    Dim lastRow As Long

    If Not WorksheetExistsSens("Sensitivity") Then
        MsgBox "Sensitivity sheet not found." & vbCrLf & _
               "Run Refresh Portfolio using the sensitivity-enabled Python file first.", _
               vbExclamation, "Portfolio Pulse"
        Exit Sub
    End If

    Set dash = ThisWorkbook.Worksheets("Dashboard")
    Set sens = ThisWorkbook.Worksheets("Sensitivity")

    lastRow = sens.Cells(sens.Rows.Count, "A").End(xlUp).Row

    On Error Resume Next
    dash.ChartObjects("SensitivityChart").Delete
    On Error GoTo ErrHandler

    Set chartObj = dash.ChartObjects.Add( _
        Left:=dash.Range("B80").Left, _
        Top:=dash.Range("B80").Top, _
        Width:=dash.Range("B80:I80").Width, _
        Height:=320)

    chartObj.Name = "SensitivityChart"

    With chartObj.Chart
        .ChartType = xlColumnClustered
        .HasTitle = True
        .ChartTitle.Text = "Allocation Sensitivity: CAGR vs. Max Drawdown"

        .SeriesCollection.NewSeries
        With .SeriesCollection(1)
            .Name = "CAGR"
            .XValues = sens.Range("A2:A" & lastRow)
            .Values = sens.Range("B2:B" & lastRow)
        End With

        .SeriesCollection.NewSeries
        With .SeriesCollection(2)
            .Name = "Max Drawdown"
            .XValues = sens.Range("A2:A" & lastRow)
            .Values = sens.Range("E2:E" & lastRow)
        End With

        .HasLegend = True
        .Legend.Position = xlLegendPositionBottom
        .Axes(xlValue).TickLabels.NumberFormat = "0.0%;[Red](0.0%)"
    End With

    With dash.Range("B97:I99")
        .UnMerge
        .Merge
        .Value = "Sensitivity analysis applies controlled +/-5% and +/-10% shifts between VTI and AGG while holding the other sleeves constant. " & _
                 "It illustrates historical risk/return trade-offs and is not an investment recommendation."
        .WrapText = True
        .Font.Italic = True
        .Font.Color = RGB(90, 90, 90)
    End With

    MsgBox "Sensitivity chart added successfully.", vbInformation, "Portfolio Pulse"
    Exit Sub

ErrHandler:
    MsgBox "Could not create sensitivity chart: " & Err.Description, _
           vbCritical, "Portfolio Pulse"
End Sub

Private Function WorksheetExistsSens(ByVal sheetName As String) As Boolean
    Dim ws As Worksheet
    On Error Resume Next
    Set ws = ThisWorkbook.Worksheets(sheetName)
    WorksheetExistsSens = Not ws Is Nothing
    On Error GoTo 0
End Function
