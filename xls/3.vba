Существует таблица Word, в которой каждая новая строка не является новой ячейкой, а просто перенос строки (Enter-ом создавали новую строку).
Я пытаюсь извлечь все строки ячейки Word в ячейки Excel. Но поскольку это не обычный перебор строк таблицы циклом, необходима помощь в создании макроса, который сможет выделить текст до переноса строки, записать его в ячейку Excel и т.д. в цикле каждую новую строку.

В этом коде мне необходимо все строки из tbl.Cell(2, 1) раскидать по ячейкам excel.

Макрос
Sub OpenWord()
    Dim objWrdApp As Object, objWrdDoc As Object, avFiles, i As Integer, tbl As Object
    avFiles = Application.GetOpenFilename _
                ("Word files(*.doc*),*.do*", 1, "Выберите таблицу", , False)
    If VarType(avFiles) = vbBoolean Then
        Exit Sub
    End If
        Set objWrdApp = CreateObject("Word.Application")
        objWrdApp.Visible = False
        Set objWrdDoc = objWrdApp.Documents.Open(avFiles)
        Set tbl = objWrdDoc.Tables(1)
        ActiveSheet.Cells(1, 1) = tbl.Cell(2, 1).Range.text       
        objWrdDoc.Close True
        objWrdApp.Quit
        Set objWrdDoc = Nothing: Set objWrdApp = Nothing
End Sub
[свернуть]

[вложение удалено администратором]
 Администратор
Administrator
Сообщения: 2 476
Записан
#1

14 ноября 2019, 12:57
Макрос
Sub OpenWord()

    Dim objWrdApp As Object, objWrdDoc As Object, avFiles, tbl As Object
    Dim var, r As Long, i As Long
   
   
    avFiles = Application.GetOpenFilename _
                ("Word files(*.doc*),*.do*", 1, "Выберите таблицу", , False)
    If VarType(avFiles) = vbBoolean Then
        Exit Sub
    End If
   
    Set objWrdApp = CreateObject("Word.Application")
    objWrdApp.Visible = False
    Set objWrdDoc = objWrdApp.Documents.Open(avFiles)
    Set tbl = objWrdDoc.Tables(1)
   
    ' Копируем данные из ворд-ячейки в переменную.
    var = tbl.Cell(2, 1).Range.Text
    ' Удаляем с конца два символа. Эти два символа есть в каждой ворд-ячейке.
        ' Один символ в виде кружка, второй символ вообще не видно.
    var = Left(var, Len(var) - 2)
    ' Разбиваем текст ячейки на части по символу "перенос строки".
    var = Split(var, Chr(13))
    ' Устанавливаем курсор на эксель-листе в нужную строку.
    r = 1
    ' Записываем части в эксель-ячейки.
    For i = 0 To UBound(var)
        ActiveSheet.Cells(r, 1) = var(i)
        r = r + 1
    Next i
   
    objWrdDoc.Close True
    objWrdApp.Quit
    Set objWrdDoc = Nothing: Set objWrdApp = Nothing
   
End Sub

