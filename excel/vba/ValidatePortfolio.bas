
Attribute VB_Name = "ValidatePortfolio"
Option Explicit

Public Function ValidateAllocations(Optional ByVal showSuccess As Boolean = True) As Boolean
    On Error GoTo ErrHandler

    Dim ws As Worksheet
    Dim r As Long
    Dim ticker As String
    Dim weight As Variant
    Dim totalWeight As Double

    Set ws = ThisWorkbook.Worksheets("Portfolio")

    totalWeight = 0

    For r = 9 To 12
        ticker = Trim$(CStr(ws.Cells(r, 2).Value))
        weight = ws.Cells(r, 3).Value

        If ticker = "" Then
            MsgBox "Missing ticker in row " & r & ".", vbExclamation, "Portfolio Pulse"
            ValidateAllocations = False
            Exit Function
        End If

        If Not IsNumeric(weight) Then
            MsgBox ticker & " weight must be numeric.", vbExclamation, "Portfolio Pulse"
            ValidateAllocations = False
            Exit Function
        End If

        If CDbl(weight) < 0 Then
            MsgBox ticker & " cannot have a negative weight.", vbExclamation, "Portfolio Pulse"
            ValidateAllocations = False
            Exit Function
        End If

        If CDbl(weight) > 1 Then
            MsgBox ticker & " cannot exceed 100%.", vbExclamation, "Portfolio Pulse"
            ValidateAllocations = False
            Exit Function
        End If

        totalWeight = totalWeight + CDbl(weight)
    Next r

    If Abs(totalWeight - 1#) > 0.0001 Then
        MsgBox "Portfolio weights must sum to 100.00%." & vbCrLf & _
               "Current total: " & Format(totalWeight, "0.00%"), _
               vbExclamation, "Portfolio Pulse"
        ValidateAllocations = False
        Exit Function
    End If

    If Not IsNumeric(ws.Range("B6").Value) Or ws.Range("B6").Value <= 0 Then
        MsgBox "Portfolio value must be greater than zero.", vbExclamation, "Portfolio Pulse"
        ValidateAllocations = False
        Exit Function
    End If

    If Not IsNumeric(ws.Range("B5").Value) Or _
       ws.Range("B5").Value < 1 Or ws.Range("B5").Value > 10 Then
        MsgBox "Risk tolerance must be between 1 and 10.", vbExclamation, "Portfolio Pulse"
        ValidateAllocations = False
        Exit Function
    End If

    ValidateAllocations = True

    If showSuccess Then
        MsgBox "Inputs are valid." & vbCrLf & _
               "Portfolio weights: " & Format(totalWeight, "0.00%"), _
               vbInformation, "Portfolio Pulse"
    End If

    Exit Function

ErrHandler:
    ValidateAllocations = False
    MsgBox "Validation error: " & Err.Description, vbCritical, "Portfolio Pulse"
End Function

Public Sub CheckAllocations()
    Call ValidateAllocations(True)
End Sub
