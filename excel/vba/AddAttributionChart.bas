Attribute VB_Name = "AddAttributionChart"
Option Explicit

Public Sub AddAttributionChart()
    On Error GoTo ErrHandler

    Dim dash As Worksheet
    Dim attr As Worksheet
    Dim chartObj As ChartObject
    Dim lastAssetRow As Long
    Dim i As Long

    If Not WorksheetExistsAttr("Attribution") Then
        MsgBox "Attribution sheet not found." & vbCrLf & _
               "Run Refresh Portfolio using the attribution-enabled Python file first.", _
               vbExclamation, "Portfolio Pulse"
        Exit Sub
    End If

    Set dash = ThisWorkbook.Worksheets("Dashboard")
    Set attr = ThisWorkbook.Worksheets("Attribution")

    lastAssetRow = 1
    For i = 2 To attr.Cells(attr.Rows.Count, "A").End(xlUp).Row
        If Trim$(attr.Cells(i, 1).Value) = "" Then Exit For
        lastAssetRow = i
    Next i

    If lastAssetRow < 2 Then
        MsgBox "No attribution data found.", vbExclamation, "Portfolio Pulse"
        Exit Sub
    End If

    On Error Resume Next
    dash.ChartObjects("AttributionChart").Delete
    On Error GoTo ErrHandler

    Set chartObj = dash.ChartObjects.Add( _
        Left:=dash.Range("B59").Left, _
        Top:=dash.Range("B59").Top, _
        Width:=dash.Range("B59:I59").Width, _
        Height:=300)

    chartObj.Name = "AttributionChart"

    With chartObj.Chart
        .ChartType = xlColumnClustered
        .HasTitle = True
        .ChartTitle.Text = "Cumulative Arithmetic Contribution by Asset"

        .SeriesCollection.NewSeries
        With .SeriesCollection(1)
            .Name = "Contribution"
            .XValues = attr.Range("A2:A" & lastAssetRow)
            .Values = attr.Range("C2:C" & lastAssetRow)
        End With

        .HasLegend = False
        .Axes(xlValue).TickLabels.NumberFormat = "0.0%;[Red](0.0%)"
    End With

    With dash.Range("B76:I77")
        .UnMerge
        .Merge
        .Value = "Attribution uses daily arithmetic contribution (portfolio weight × asset return). " & _
                 "It is designed to reconcile daily portfolio returns and should not be interpreted as Brinson attribution."
        .WrapText = True
        .Font.Italic = True
        .Font.Color = RGB(90, 90, 90)
    End With

    MsgBox "Attribution chart added successfully.", vbInformation, "Portfolio Pulse"
    Exit Sub

ErrHandler:
    MsgBox "Could not create attribution chart: " & Err.Description, _
           vbCritical, "Portfolio Pulse"
End Sub

Private Function WorksheetExistsAttr(ByVal sheetName As String) As Boolean
    Dim ws As Worksheet
    On Error Resume Next
    Set ws = ThisWorkbook.Worksheets(sheetName)
    WorksheetExistsAttr = Not ws Is Nothing
    On Error GoTo 0
End Function
