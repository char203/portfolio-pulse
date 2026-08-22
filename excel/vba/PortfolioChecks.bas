Attribute VB_Name = "PortfolioChecks"
Option Explicit

Public Sub ValidatePortfolioWeights()
    Dim ws As Worksheet
    Dim totalWeight As Double
    Set ws = ThisWorkbook.Worksheets("Portfolio")

    totalWeight = Application.WorksheetFunction.Sum(ws.Range("C6:C9"))

    If Abs(totalWeight - 1#) > 0.0001 Then
        MsgBox "Portfolio weights must sum to 100%. Current total: " & Format(totalWeight, "0.0%"), vbExclamation, "Portfolio Pulse"
    Else
        MsgBox "Portfolio weights sum to 100%.", vbInformation, "Portfolio Pulse"
    End If
End Sub
