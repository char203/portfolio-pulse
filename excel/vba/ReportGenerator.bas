Attribute VB_Name = "ReportGenerator"
Option Explicit

Public Sub GeneratePortfolioReport()
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Worksheets("Dashboard")
    ws.Calculate
    ws.Activate
    MsgBox "Dashboard refreshed. PDF export will be added after the model is validated.", vbInformation, "Portfolio Pulse"
End Sub
