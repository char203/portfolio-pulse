
Attribute VB_Name = "GenerateReport"
Option Explicit

Public Sub GeneratePortfolioReport()
    On Error GoTo ErrHandler

    Dim ws As Worksheet
    Dim pdfPath As String

    Set ws = ThisWorkbook.Worksheets("Dashboard")

    pdfPath = ThisWorkbook.Path & "/Portfolio_Pulse_Report.pdf"

    ws.PageSetup.Orientation = xlLandscape
    ws.PageSetup.Zoom = False
    ws.PageSetup.FitToPagesWide = 1
    ws.PageSetup.FitToPagesTall = 1

    ws.ExportAsFixedFormat _
        Type:=xlTypePDF, _
        Filename:=pdfPath, _
        Quality:=xlQualityStandard, _
        IncludeDocProperties:=True, _
        IgnorePrintAreas:=False, _
        OpenAfterPublish:=True

    MsgBox "Report created:" & vbCrLf & pdfPath, vbInformation, "Portfolio Pulse"
    Exit Sub

ErrHandler:
    MsgBox "Report generation failed: " & Err.Description, vbCritical, "Portfolio Pulse"
End Sub
