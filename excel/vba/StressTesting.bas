Attribute VB_Name = "StressTesting"
Option Explicit

Public Sub RunStressTest()
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Worksheets("Stress Tests")
    ws.Calculate
    MsgBox "Historical stress-test outputs refreshed.", vbInformation, "Portfolio Pulse"
End Sub
