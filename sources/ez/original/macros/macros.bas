olevba 0.60.2 on Python 3.13.3 - http://decalage.info/python/oletools
===============================================================================
FILE: EZ template.dot
Type: OLE
-------------------------------------------------------------------------------
VBA MACRO ThisDocument.cls 
in file: EZ template.dot - OLE stream: 'Macros/VBA/ThisDocument'
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
(empty macro)
-------------------------------------------------------------------------------
VBA MACRO EZ_Macros.bas 
in file: EZ template.dot - OLE stream: 'Macros/VBA/EZ_Macros'
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
' This document contains nine macros for fixing up the music in documents written in Microsoft Word using
'    the "EZ" Byzantine music fonts. The names of the macros are: "MoveUp", "MoveDown", "MoveLeft",
'    "MoveRight", "Justify", "PolishNotes", "PolishNotes1", "PolishNotes1b", "PolishNotes2", "PolishNotes2b",
'    "MakeNotesRed", "ExpandLine", "CompressLine", and "MakeIsonBlue"
'
'    Last changes made: April 15, 2007
'
'    For more infomation about how to use these macros, see the file "INSTRUCTIONS.doc"
'
'    If you encounter any problems with these macros please contact me at: byzmusic@yahoo.com

Sub MoveUp()
'
' MoveUp Macro
' Macro recorded 1/3/2005 by Father Ephraim
'
Dim y
    
    For Each y In Selection.Characters
        y.Font.Position = y.Font.Position + 1
    Next

End Sub
'
Sub MoveDown()
'
' MoveDown Macro
' Macro recorded 1/3/2005 by Father Ephraim
'
Dim y
    
    For Each y In Selection.Characters
        y.Font.Position = y.Font.Position - 1
    Next

End Sub
'
Sub MoveLeft()
'
' MoveLeft Macro
' Macro recorded 1/3/2005 by Father Ephraim
'
Dim y

    Selection.MoveLeft Unit:=wdCharacter, Count:=1
    Selection.MoveLeft Unit:=wdCharacter, Count:=1, Extend:=wdExtend
    
    For Each y In Selection.Characters
        y.Font.Spacing = y.Font.Spacing - 1
    Next
    
    Selection.MoveRight Unit:=wdCharacter, Count:=1
    Selection.MoveRight Unit:=wdCharacter, Count:=1, Extend:=wdExtend
    
    For Each y In Selection.Characters
        y.Font.Spacing = y.Font.Spacing + 1
    Next
    
End Sub
'
Sub MoveRight()
'
' MoveRight Macro
' Macro recorded 1/3/2005 by Father Ephraim
'
Dim y

    Selection.MoveLeft Unit:=wdCharacter, Count:=1
    Selection.MoveLeft Unit:=wdCharacter, Count:=1, Extend:=wdExtend
    
    For Each y In Selection.Characters
        y.Font.Spacing = y.Font.Spacing + 1
    Next
    
    Selection.MoveRight Unit:=wdCharacter, Count:=1
    Selection.MoveRight Unit:=wdCharacter, Count:=1, Extend:=wdExtend
    
    For Each y In Selection.Characters
        y.Font.Spacing = y.Font.Spacing - 1
    Next
    
End Sub
'
Sub Justify()
'
' Justify Macro
' Macro recorded 1/4/2005 by Father Ephraim
'
' The following macro replaces spaces in the EZ Psaltica font with spaces using the Tahoma font
'   with the font size set at "1", and then it justifies the spacing. (The macros need to change
'   the font name to make justification possible.)
'
' The following 90 lines of code insert spaces before all characters that should be preceded by
'   a space, just in case the user forgot to insert any of those spaces.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61488) & ChrW(61552) & ChrW(61489) & ChrW(61490) & _
             ChrW(61491) & ChrW(61492) & ChrW(61493) & ChrW(61494) & ChrW(61495) _
             & ChrW(61496) & ChrW(61497) & ChrW(61536) & ChrW(61501) & ChrW( _
            61553) & ChrW(61559) & ChrW(61541) & ChrW(61554) & ChrW(61556) & _
            ChrW(61561) & ChrW(61557) & ChrW(61545) & ChrW(61473) & ChrW(61504) _
            & ChrW(61535) & ChrW(61481) & ChrW(61485) & ChrW(61475) & ChrW(61476 _
            ) & ChrW(61477) & ChrW(61534) & ChrW(61478) & ChrW(61482) & ChrW( _
            61480) & ChrW(61521) & ChrW(61527) & ChrW(61509) & ChrW(61519) & _
            ChrW(61551) & ChrW(61548) & ChrW(61516) & ChrW(61520) & ChrW(61513) _
            & ChrW(61525) & ChrW(61529) & ChrW(61524) & ChrW(61522) & ChrW(61485 _
            ) & ChrW(61501) & ChrW(61539) & ChrW(61558) & ChrW(61538) & ChrW( _
            61550) & ChrW(61549) & ChrW(61484) & ChrW(61486) & ChrW(61564) & _
            ChrW(61483) & "]"
        .Font.NameOther = "EZ Psaltica"
        .Replacement.Text = ChrW(61472) & "^&"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = False
        .MatchWholeWord = False
        .MatchAllWordForms = False
        .MatchSoundsLike = False
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61488) & ChrW(61489) & ChrW(61490) & ChrW(61491) & _
             ChrW(61492) & ChrW(61480) & ChrW(61552) & ChrW(61553) & ChrW(61559) _
             & ChrW(61541) & ChrW(61554) & ChrW(61557) & ChrW(61545) & ChrW( _
            61551) & ChrW(61501) & ChrW(61481) & ChrW(61473) & ChrW(61504) & _
            ChrW(61521) & ChrW(61527) & ChrW(61509) & ChrW(61522) & ChrW(61477) _
            & ChrW(61534) & ChrW(61561) & ChrW(61556) & ChrW(61493) & ChrW(61494 _
            ) & ChrW(61495) & ChrW(61496) & ChrW(61497) & ChrW(61513) & ChrW( _
            61524) & ChrW(61529) & ChrW(61525) & ChrW(61519) & ChrW(61532) & _
            ChrW(61533) & ChrW(61565) & ChrW(61485) & ChrW(61535) & ChrW(61531) _
            & ChrW(61563) & ChrW(61520) & ChrW(61505) & ChrW(61537) & ChrW(61523 _
            ) & ChrW(61555) & ChrW(61562) & ChrW(61560) & ChrW(61528) & ChrW( _
            61530) & ChrW(61550) & ChrW(61549) & ChrW(61484) & "]"
        .Font.NameOther = "EZ Special-I"
        .Replacement.Text = ChrW(61472) & "^&"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = False
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61485) & ChrW(61497) & ChrW(61488) & ChrW(61481) & _
             ChrW(61535) & ChrW(61533) & "]"
        .Font.NameOther = "EZ Special-II"
        .Replacement.Text = ChrW(61472) & "^&"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = False
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61545) & ChrW(61513) & ChrW(61489) & ChrW(61490) & _
             ChrW(61491) & ChrW(61492) & ChrW(61493) & ChrW(61494) & ChrW(61495) _
             & ChrW(61496) & ChrW(61497) & ChrW(61521) & ChrW(61527) & ChrW( _
            61509) & ChrW(61473) & ChrW(61536) & ChrW(61485) & ChrW(61504) & _
            ChrW(61475) & ChrW(61476) & ChrW(61520) & ChrW(61551) & ChrW(61519) _
            & ChrW(61548) & ChrW(61516) & ChrW(61501) & ChrW(61477) & ChrW(61534 _
            ) & ChrW(61525) & ChrW(61529) & ChrW(61524) & ChrW(61522) & ChrW( _
            61478) & ChrW(61482) & ChrW(61480) & ChrW(61546) & ChrW(61514) & _
            ChrW(61626) & ChrW(61535) & ChrW(61532) & ChrW(61552) & ChrW(61483) _
            & "]"
        .Font.NameOther = "EZ Oxeia"
        .Replacement.Text = ChrW(61472) & "^&"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = False
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
'
'  The next eleven lines change two consecutive spaces into one space
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61472) & ChrW(61472)
        .Replacement.Text = ChrW(61472)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchWildcards = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    Selection.Find.Execute Replace:=wdReplaceAll
'
' These last lines of code change those spaces into the Tahoma font.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61472)
        With .Replacement
            .Text = " "
            .Font.Size = 1
            .Font.Name = "Tahoma"
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = False
        .MatchWholeWord = False
        .MatchWildcards = False
        .MatchSoundsLike = False
        .MatchAllWordForms = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.EndKey Unit:=wdStory
    
    Selection.ParagraphFormat.Alignment = wdAlignParagraphJustify

End Sub
'
'
'
'
'
'
Sub PolishNotes()

' The following macro will run the two large macros "PolishNotes1" and
'  "PolishNotes2". If no text is selected before running this macro, it
'  will polish the entire document. But if some text is selected, it will
'  only polish the notes selected. In order to do this, it creates a new
'  document as a temporary scratch pad. When it closes this scratch pad,
'  Word asks the user if he wants the changes to this scratch pad to be
'  saved. The user should respond "no", since this scratch pad is useless
'  for him.

Dim SelectedText

If Selection.Type = wdSelectionIP Then
   SelectedText = 0

'  This is a flag variable which equals zero when no text is selected,
'   in which case the next five lines of code are skipped, as well as the
'   last four lines of code.

  Else
    SelectedText = 1
    Selection.Copy
    Documents.Add DocumentType:=wdNewBlankDocument
'    Selection.PasteAndFormat (wdPasteDefault)
   Selection.Paste
End If
 
 PolishNotes1
 PolishNotes1b
 PolishNotes2
 PolishNotes2b

'
' The following 32 lines of code slightly lower a gorgon that
'  is beneath an elaphron.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61504) & ChrW(61560)
        .Font.NameOther = "EZ Psaltica"
        With .Replacement
        .Text = "^&"
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61560)
        .Font.NameOther = "EZ Psaltica"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Position = -1
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.WholeStory
    Selection.Font.Emboss = False

'
' The following 62 lines of code shift the number "3" or "4" slightly
'  to the left when followed by a klasma so that they aren't so close.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "?[" & ChrW(61491) & ChrW(61492) & "]" & ChrW(61537)
        With .Replacement
        .Text = "^&"
        .Font.Engrave = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61491) & ChrW(61492) & "]"
        .Font.Engrave = True
        With .Replacement
        .Text = "^&"
        .Font.Spacing = 1
        .Font.Engrave = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61537)
        .Font.Engrave = True
        With .Replacement
        .Text = "^&"
        .Font.Engrave = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "^?"
        .Font.Engrave = True
        With .Replacement
        .Text = "^&"
        .Font.Engrave = False
        .Font.Spacing = -1
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 94 lines of code shift the aple and the antikenoma to the right when they are
'   beneath a petaste that is beneath an ypsele (i.e., a jump of four).
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61554) & ChrW(61474) & ChrW(61499)
        .Font.NameOther = "EZ Psaltica"
        .Replacement.Text = ChrW(61554) & ChrW(61499) & ChrW(61474)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61554) & ChrW(61499) & ChrW(61474)
        .Font.NameOther = "EZ Psaltica"
        With .Replacement
            .Text = ChrW(61554) & ChrW(61498) & ChrW(61474)
            .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61554)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Spacing = -5
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61498)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Spacing = 5
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61474)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Scaling = 90
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
'
' The following 94 lines of code shift the aple and the antikenoma to the right when they are
'   beneath a petaste that is beneath an ypsele on the left (i.e., a jump of five).
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61556) & ChrW(61474) & ChrW(61499)
        .Font.NameOther = "EZ Psaltica"
        .Replacement.Text = ChrW(61556) & ChrW(61499) & ChrW(61474)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61556) & ChrW(61499) & ChrW(61474)
        .Font.NameOther = "EZ Psaltica"
        With .Replacement
            .Text = ChrW(61556) & ChrW(61498) & ChrW(61474)
            .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61556)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Spacing = -5
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61498)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Spacing = 5
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61474)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Scaling = 90
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 94 lines of code shift the aple and the antikenoma to the right when they are
'   beneath a petaste that is beneath an ypsele and a kentema (i.e., a jump of six).
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61561) & ChrW(61474) & ChrW(61499)
        .Font.NameOther = "EZ Psaltica"
        .Replacement.Text = ChrW(61561) & ChrW(61499) & ChrW(61474)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61561) & ChrW(61499) & ChrW(61474)
        .Font.NameOther = "EZ Psaltica"
        With .Replacement
            .Text = ChrW(61561) & ChrW(61498) & ChrW(61474)
            .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61561)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Spacing = -5
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61498)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Spacing = 5
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61474)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Scaling = 90
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 94 lines of code shift the aple and the antikenoma to the right when they are
'   beneath a petaste that is beneath kentemata beneath and ypsele (i.e., a jump of seven).
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61557) & ChrW(61474) & ChrW(61499)
        .Font.NameOther = "EZ Psaltica"
        .Replacement.Text = ChrW(61557) & ChrW(61499) & ChrW(61474)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61557) & ChrW(61499) & ChrW(61474)
        .Font.NameOther = "EZ Psaltica"
        With .Replacement
            .Text = ChrW(61557) & ChrW(61498) & ChrW(61474)
            .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61557)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Spacing = -5
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61498)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Spacing = 5
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61474)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Scaling = 90
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

If SelectedText = 0 Then Exit Sub
    Selection.MoveLeft Unit:=wdCharacter, Count:=1, Extend:=wdExtend
    Selection.Cut
    ActiveDocument.Close
'    Selection.PasteAndFormat (wdPasteDefault)
    Selection.Paste

End Sub

Sub PolishNotes1()
'
' PolishNotes1 Macro
' This macro lowers all martyries, shifts the klasma beneath a petaste to its proper position,
'     moves the kentemata to the left when they collide with a psefeston beneath an oligon,
'     adds a dot to the right of a gorgon that is above the kentemata when followed by a vareia
'     and an ison, lowers the klasma, gorgon, digorgon, and trigorgon on top of an apostrophos,
'     and automatically shifts a gorgon to the left when it is not directly above the kentemata
'     as it should be, and does many other such changes to polish relative note positions.
' As of 3/20/05, this macro has been broken up into two macros: "PolishNotes1" and "PolishNotes2"
'     because there were so many lines of code, that the compiler could not handle it as a single
'     macro. Both of these macros are executed by the macro "PolishNotes".
'
' If you notice any error in these macros, please inform me at: frephraim@fastmail.fm
'
'
' The first 5 lines of code remove any previous formatting so that none of the music is raised,
'   condensed, or expanded.
'
    Selection.WholeStory
    With Selection.Font
        .Spacing = 0
        .Position = 0
    End With

' The following 61 lines of code shift the syndesmos to the right when preceded by an oligon
'   with kentemata and a gorgon.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61548) & ChrW(61533)
        With .Replacement
            .Text = "^&"
            .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True




    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61548)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Color = wdColorBlack
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True




    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61533)
        .Font.Emboss = True
        With .Replacement
            .Text = "\"
            .Font.Emboss = False
            .Font.Name = "EZ Special-II"
            .Font.Color = wdColorBlack
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
        .MatchWildcards = False
     End With
     Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 76 lines of code fix a gorgon that is beneath a elafron that has an apostrophos
'   in it.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61475) & ChrW(61528)
        .Replacement.Text = ChrW(61475) & ChrW(61560)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True




    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61475) & ChrW(61560)
        With .Replacement
            .Text = "^&"
            .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True




    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61475)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
'            .Font.Color = wdColorBlack
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True




    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.Emboss = True
        .Text = ChrW(61560)
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Position = -4
'            .Font.Color = wdColorBlack
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True




    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 63 lines of code lower all martyries
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Psaltica"
        .Text = "[" & ChrW(61539) & ChrW(61558) & ChrW(61538) & ChrW(61550) & _
             ChrW(61549) & ChrW(61484) & ChrW(61486) & ChrW(61487) & ChrW(61507) _
             & ChrW(61526) & ChrW(61506) & ChrW(61518) & ChrW(61517) & ChrW( _
            61500) & ChrW(61502) & ChrW(61503) & "]"
         With .Replacement
            .Text = "^&"
            .Font.Position = -3
         End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Special-I"
        .Text = "[" & ChrW(61505) & ChrW(61537) & ChrW(61523) & ChrW(61555) & _
             ChrW(61530) & ChrW(61562) & ChrW(61528) & ChrW(61560) & ChrW(61518) _
             & ChrW(61550) & ChrW(61517) & ChrW(61549) & ChrW(61500) & ChrW( _
            61484) & ChrW(61502) & ChrW(61486) & ChrW(61503) & ChrW(61487) & "]"
         With .Replacement
            .Text = "^&"
            .Font.Position = -3
         End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Fthora"
        .Text = ChrW(61609)
         With .Replacement
            .Text = "^&"
            .Font.Position = -3
         End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
        .MatchAllWordForms = False
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 14 lines of code lower the soft chromatic
'  martyria that is placed beneath Ga.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61609)
        .Font.NameOther = "EZ Fthora"
        With .Replacement
        .Text = "^&"
        .Font.Position = -3
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
'
' The following 65 lines of code replace a syndesmos followed by a psefiston
'  with special characters that replace these two symbols
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61533) & ChrW(61479)
        .Font.NameOther = "EZ Psaltica"
        .Replacement.Text = ChrW(61479) & ChrW(61533)
        .Forward = True
        .Wrap = wdFindContinue
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61479) & ChrW(61533)
        .Font.NameOther = "EZ Psaltica"
        With .Replacement
        .Font.Emboss = True
        .Text = "^&"
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61479)
        .Font.Emboss = True
        With .Replacement
        .Font.NameOther = "EZ Oxeia"
        .Text = ChrW(61487)
        .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61533)
        .Font.Emboss = True
        With .Replacement
        .Font.Emboss = False
        .Font.NameOther = "EZ Oxeia"
        .Text = "^&"
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 30 lines of code shift the kentemata to the left when they
'      collide with a psefeston beneath an oligon.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61551) & ChrW(61537) & ChrW(61479)
        .Replacement.Text = ChrW(61551) & ChrW(61479) & ChrW(61537)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61551) & ChrW(61555) & ChrW(61479)
        .Replacement.Text = ChrW(61551) & ChrW(61479) & ChrW(61555)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Psaltica"
        .Text = ChrW(61551) & ChrW(61479)
        .Replacement.Text = ChrW(61646) & ChrW(61479)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
'
' The following 11 lines of code change the combo: apostrophos-aple-gorgon to: the combo:
'   apostrophos-gorgon-aple. This doesn't change the look of things, but it gets the notes
'   in the order that the macros will need them to be in order to lower the gorgon.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61473) & ChrW(61498) & ChrW(61523)
        .Replacement.Text = ChrW(61473) & ChrW(61523) & ChrW(61498)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
'
' The following 61 lines of code shift the gorgon slightly to the left when it is above kentemata
' that are above an oligon that has another note to the left of the kentemata also on the oligon.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61522) & ChrW(61524) & ChrW(61529) & ChrW(61525) & _
             ChrW(61520) & "]" & ChrW(61523)
        With .Replacement
            .Text = "^&"
            .Font.Spacing = -2
            .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61523)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Spacing = 2
            .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61522) & ChrW(61524) & ChrW(61529) & ChrW(61525) & _
             ChrW(61520) & "]"
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 358 lines of code add a dot to the right of a gorgon that is above the kentemata
'   when followed by a vareia and an ison, regardless of whether or not there is a single space
'   between them.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61523) & ChrW(61472) & ChrW(61532) & ChrW(61472)
        .Replacement.Text = ChrW(61523) & ChrW(61532)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
'
'
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61520) & ChrW(61523) & ChrW(61532) & ChrW(61488)
        .Replacement.Text = ChrW(61520) & ChrW(61512) & ChrW(61532) & ChrW( _
            61488)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61512) & ChrW(61532) & ChrW(61488)
        With .Replacement
            .Text = ChrW(61512) & ChrW(61472) & ChrW(61532) & ChrW(61488)
            .Font.Name = "EZ Special-I"
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61472) & ChrW(61532) & ChrW(61488)
        With .Replacement
            .Text = ChrW(61472) & ChrW(61532) & ChrW(61488)
            .Font.Name = "EZ Psaltica"
            .Font.Spacing = 0
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
'
'
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61548) & ChrW(61472) & ChrW(61532) & ChrW(61472)
        .Replacement.Text = ChrW(61548) & ChrW(61532)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61548) & ChrW(61532) & ChrW(61488)
        .Replacement.Text = ChrW(61655) & ChrW(61544) & ChrW(61472) & ChrW(61532) & ChrW( _
            61488)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61544) & ChrW(61472) & ChrW(61532) & ChrW(61488)
        With .Replacement
            .Text = ChrW(61544) & ChrW(61472) & ChrW(61532) & ChrW(61488)
            .Font.Name = "EZ Special-I"
            .Font.Position = 3
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61472) & ChrW(61532) & ChrW(61488)
        With .Replacement
            .Text = ChrW(61472) & ChrW(61532) & ChrW(61488)
            .Font.Name = "EZ Psaltica"
            .Font.Position = 0
            .Font.Spacing = 0
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
'
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61525) & ChrW(61523) & ChrW(61532) & ChrW(61488)
        .Replacement.Text = ChrW(61525) & ChrW(61512) & ChrW(61532) & ChrW( _
            61488)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61512) & ChrW(61532) & ChrW(61488)
        With .Replacement
            .Text = ChrW(61512) & ChrW(61472) & ChrW(61532) & ChrW(61488)
            .Font.Name = "EZ Special-I"
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61472) & ChrW(61532) & ChrW(61488)
        With .Replacement
            .Text = ChrW(61472) & ChrW(61532) & ChrW(61488)
            .Font.Name = "EZ Psaltica"
            .Font.Spacing = 0
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
'
'
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61529) & ChrW(61523) & ChrW(61532) & ChrW(61488)
        .Replacement.Text = ChrW(61529) & ChrW(61512) & ChrW(61472) & ChrW(61532) & ChrW( _
            61488)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61512) & ChrW(61472) & ChrW(61532) & ChrW(61488)
        With .Replacement
            .Text = ChrW(61512) & ChrW(61472) & ChrW(61532) & ChrW(61488)
            .Font.Name = "EZ Special-I"
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61472) & ChrW(61532) & ChrW(61488)
        With .Replacement
            .Text = ChrW(61472) & ChrW(61532) & ChrW(61488)
            .Font.Name = "EZ Psaltica"
            .Font.Spacing = 0
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
'
'
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61524) & ChrW(61523) & ChrW(61532) & ChrW(61488)
        .Replacement.Text = ChrW(61524) & ChrW(61512) & ChrW(61532) & ChrW( _
            61488)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61512) & ChrW(61532) & ChrW(61488)
        With .Replacement
            .Text = ChrW(61512) & ChrW(61472) & ChrW(61532) & ChrW(61488)
            .Font.Name = "EZ Special-I"
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61472) & ChrW(61532) & ChrW(61488)
        With .Replacement
            .Text = ChrW(61472) & ChrW(61532) & ChrW(61488)
            .Font.Name = "EZ Psaltica"
            .Font.Spacing = 0
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
'
'
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61522) & ChrW(61523) & ChrW(61532) & ChrW(61488)
        .Replacement.Text = ChrW(61522) & ChrW(61512) & ChrW(61532) & ChrW( _
            61488)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61512) & ChrW(61532) & ChrW(61488)
        With .Replacement
            .Text = ChrW(61512) & ChrW(61472) & ChrW(61532) & ChrW(61488)
            .Font.Name = "EZ Special-I"
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61472) & ChrW(61532) & ChrW(61488)
        With .Replacement
            .Text = ChrW(61472) & ChrW(61532) & ChrW(61488)
            .Font.Name = "EZ Psaltica"
            .Font.Spacing = 0
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 33 lines of code lower the gorgon and the digorgon when they
'   are placed above an apostrophos.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61473) & "[" & ChrW(61523) & ChrW(61508) & "]"
        With .Replacement
            .Text = "^&"
            .Font.Position = -3
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    ActiveWindow.ActivePane.VerticalPercentScrolled = 0
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61473)
        .Font.Position = -3
        With .Replacement
            .Text = "^&"
            .Font.Position = 0
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 108 lines of code move the kentemata to the left when they collide with an omalon
'   beneath an oligon.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61551) & ChrW(61555) & ChrW(61563)
        .Replacement.Text = ChrW(61551) & ChrW(61563) & ChrW(61555)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61551) & ChrW(61543) & ChrW(61563)
        .Replacement.Text = ChrW(61551) & ChrW(61563) & ChrW(61543)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61551) & ChrW(61511) & ChrW(61563)
        .Replacement.Text = ChrW(61551) & ChrW(61563) & ChrW(61511)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61551) & ChrW(61514) & ChrW(61563)
        With .Replacement
            .Text = ChrW(61551) & ChrW(61563) & ChrW(61514)
            .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61514)
        .Font.Emboss = True
        With .Replacement
            .Text = ChrW(61514)
            .Font.Emboss = False
            .Font.Name = "EZ Special-I"
            .Font.Color = wdColorBlack
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61551) & ChrW(61563)
        .Font.Emboss = True
        With .Replacement
            .Text = ChrW(61551) & ChrW(61563)
            .Font.Emboss = False
'           .Font.Color = wdColorBlack
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61551) & ChrW(61537) & ChrW(61563)
        .Replacement.Text = ChrW(61551) & ChrW(61563) & ChrW(61537)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61551) & ChrW(61563)
        .Replacement.Text = ChrW(61646) & ChrW(61563)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The next 79 lines of code shift the klasma beneath a petaste to its proper
'   position (more to the right)
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Psaltica"
        .Text = ChrW(61553) & ChrW(61562)
        .Replacement.Text = ChrW(61553) & ChrW(61585)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61521) & ChrW(61562)
        .Replacement.Text = ChrW(61521) & ChrW(61585)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61527) & ChrW(61562)
        .Replacement.Text = ChrW(61527) & ChrW(61585)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61509) & ChrW(61562)
        .Replacement.Text = ChrW(61509) & ChrW(61585)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61559) & ChrW(61562)
        .Replacement.Text = ChrW(61559) & ChrW(61585)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61541) & ChrW(61562)
        .Replacement.Text = ChrW(61541) & ChrW(61585)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61552) & ChrW(61562)
        .Replacement.Text = ChrW(61552) & ChrW(61585)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61535) & ChrW(61562)
        With .Replacement
            .Text = "^&"
            .Font.NameOther = "EZ Special-II"
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 72 lines of code shift a psefeston to the right when it collides with a klasma
'   beneath a petaste.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61585) & ChrW(61479) & ChrW(61472) & ChrW(61473)
        .Replacement.Text = ChrW(61585) & ChrW(61479) & ChrW(61473)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61585) & ChrW(61479) & ChrW(61473)
        With .Replacement
        .Text = ChrW(61585) & ChrW(61473) & ChrW(61479)
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchAllWordForms = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61585)
        .Font.Emboss = True
        With .Replacement
        .Font.Emboss = False
        .Text = "^&"
        .Font.Spacing = 2
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61473)
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = -10
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61479)
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = 10
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 40 lines of code shift a gorgon down that is above an oligon with a kentema on
'   top (i.e., a jump of three)
'
Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61491) & ChrW(61474) & ChrW(61523)
        .Replacement.Text = ChrW(61491) & ChrW(61523) & ChrW(61474)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61491) & ChrW(61523)
        With .Replacement
            .Text = "^&"
            .Font.Position = -3
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61491)
        With .Replacement
            .Text = "^&"
            .Font.Position = 0
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

End Sub

Sub PolishNotes1b()

'
' The following 54 lines of code shift a gorgon that is after a rest so that it is
'  aligned exactly above the aple.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61564) & ChrW(61523)
        .Replacement.Text = ChrW(61564) & ChrW(61555)
        .Forward = True
        .Wrap = wdFindContinue
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61564) & ChrW(61555)
        With .Replacement
        .Text = "^&"
        .Font.Spacing = 12
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61555)
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Spacing = -12
        .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61564)
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 259 lines of code add an aple to a gorgon above kentemata when
'   followed by an ison that is not preceded by a vareia.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Psaltica"
        .Text = ChrW(61523) & ChrW(61472) & ChrW(61488)
        .Font.Position = 0
        .Replacement.Text = ChrW(61523) & ChrW(61488)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
'
'
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61520) & ChrW(61523) & ChrW(61488)
        With .Replacement
            .Text = ChrW(61520) & ChrW(61512) & ChrW( _
            61472) & ChrW(61488)
            .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61512)
        .Font.Emboss = True
        With .Replacement
            .Text = ChrW(61512)
            .Font.Name = "EZ Special-I"
            .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61488) & ChrW(61472) & "]"
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Name = "EZ Psaltica"
            .Font.Emboss = False
            .Font.Spacing = 0
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61520)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Name = "EZ Psaltica"
            .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
'
'
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61525) & ChrW(61523) & ChrW(61488)
        .Font.NameOther = "EZ Psaltica"
        With .Replacement
            .Text = ChrW(61525) & ChrW(61512) & ChrW( _
            61472) & ChrW(61488)
            .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61512)
        .Font.Emboss = True
        With .Replacement
            .Text = ChrW(61512)
            .Font.Name = "EZ Special-I"
            .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61488) & ChrW(61472) & "]"
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Name = "EZ Psaltica"
            .Font.Emboss = False
            .Font.Spacing = 0
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61525)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Name = "EZ Psaltica"
            .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
'
'
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61529) & ChrW(61523) & ChrW(61488)
        With .Replacement
            .Text = ChrW(61529) & ChrW(61512) & ChrW( _
            61472) & ChrW(61488)
            .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61512)
        .Font.Emboss = True
        With .Replacement
            .Text = ChrW(61512)
            .Font.Name = "EZ Special-I"
            .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61488) & ChrW(61472) & "]"
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Name = "EZ Psaltica"
            .Font.Emboss = False
            .Font.Spacing = 0
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61529)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Name = "EZ Psaltica"
            .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
'
'
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61524) & ChrW(61523) & ChrW(61488)
        With .Replacement
            .Text = ChrW(61524) & ChrW(61512) & ChrW( _
            61472) & ChrW(61488)
            .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61512)
        .Font.Emboss = True
        With .Replacement
            .Text = ChrW(61512)
            .Font.Name = "EZ Special-I"
            .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61488) & ChrW(61524) & ChrW(61472) & "]"
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Name = "EZ Psaltica"
            .Font.Emboss = False
            .Font.Spacing = 0
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61524)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Name = "EZ Psaltica"
            .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
'
'
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61522) & ChrW(61523) & ChrW(61488)
        With .Replacement
            .Text = ChrW(61522) & ChrW(61512) & ChrW( _
            61472) & ChrW(61488)
            .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61512)
        .Font.Emboss = True
        With .Replacement
            .Text = ChrW(61512)
            .Font.Name = "EZ Special-I"
            .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61488) & ChrW(61472) & "]"
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Name = "EZ Psaltica"
            .Font.Emboss = False
            .Font.Spacing = 0
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61522)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Name = "EZ Psaltica"
            .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 32 lines of code slightly lower a gorgon that
'  is beneath an elaphron.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61504) & ChrW(61560)
        .Font.NameOther = "EZ Psaltica"
        With .Replacement
        .Text = "^&"
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61560)
        .Font.NameOther = "EZ Psaltica"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Position = -1
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.WholeStory
    Selection.Font.Emboss = False

'
' The following 62 lines of code shift the number "3" or "4" slightly
'  to the left when followed by a klasma so that they aren't so close.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "?[" & ChrW(61491) & ChrW(61492) & "]" & ChrW(61537)
        With .Replacement
        .Text = "^&"
        .Font.Engrave = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61491) & ChrW(61492) & "]"
        .Font.Engrave = True
        With .Replacement
        .Text = "^&"
        .Font.Spacing = 1
        .Font.Engrave = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61537)
        .Font.Engrave = True
        With .Replacement
        .Text = "^&"
        .Font.Engrave = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "^?"
        .Font.Engrave = True
        With .Replacement
        .Text = "^&"
        .Font.Engrave = False
        .Font.Spacing = -1
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 45 lines of code reposition a gorgon that is beneath
'  a hamele so that they are aligned better.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61476) & ChrW(61528)
        .Font.NameOther = "EZ Psaltica"
        With .Replacement
        .Text = "^&"
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61476)
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = -3
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61528)
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Position = 2
        .Font.Spacing = 3
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 45 lines of code lower a diple that is beneath
'  a jump down of three so that they don't collide.
'
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61475) & ChrW(61547)
        .Font.NameOther = "EZ Psaltica"
        With .Replacement
        .Text = "^&"
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61475)
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61547)
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Position = -2
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 15 lines of code shift an aple down so that
'  it doesn't collide with an antikenoma beneath a jump of 2
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61501) & ChrW(61499)
        .Font.NameOther = "EZ Psaltica"
        With .Replacement
         .Text = ChrW(61501)
         .Font.NameOther = "EZ Special-I"
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .MatchCase = True
        .MatchWholeWord = False
        .MatchWildcards = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 60 lines of code reposition a diple that
'  is beneath a hamele so that they are aligned better.
'

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61476) & ChrW(61547)
        .Font.NameOther = "EZ Psaltica"
        .Replacement.Text = ChrW(61476) & ChrW(61515)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
        .MatchWholeWord = False
        .MatchWildcards = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61476) & ChrW(61515)
        .Font.NameOther = "EZ Psaltica"
        With .Replacement
        .Text = "^&"
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61476)
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = -4
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61515)
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = 4
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 46 lines of code shift to the left an apostrophe
'  that is after a chromatic martyria
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61503) & ChrW(61487)
        .Font.NameOther = "EZ Psaltica"
        With .Replacement
        .Text = "^&"
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61503)
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = -2
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61487)
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = 2
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 45 lines of code shift a klasma to the right when
' it is to the right of an ypsele above an oligon (a jump of five
' held for two beats) so that they don't collide
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61493) & ChrW(61537)
        .Font.NameOther = "EZ Psaltica"
        With .Replacement
        .Text = "^&"
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61493)
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = 2
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61537)
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = -2
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 94 lines of code shift the aple and the antikenoma to the right when they are
'   beneath a petaste that is beneath an oligon (i.e., a jump of two).
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61559) & ChrW(61474) & ChrW(61499)
        .Font.NameOther = "EZ Psaltica"
        .Replacement.Text = ChrW(61559) & ChrW(61499) & ChrW(61474)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61559) & ChrW(61499) & ChrW(61474)
        .Font.NameOther = "EZ Psaltica"
        With .Replacement
            .Text = ChrW(61559) & ChrW(61498) & ChrW(61474)
            .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61559)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Spacing = -5
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61498)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Spacing = 5
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61474)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Scaling = 90
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 94 lines of code shift the aple and the antikenoma to the right when they are
'   beneath a petaste that is beneath a kentema (i.e., a jump of three).
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61541) & ChrW(61474) & ChrW(61499)
        .Font.NameOther = "EZ Psaltica"
        .Replacement.Text = ChrW(61541) & ChrW(61499) & ChrW(61474)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61541) & ChrW(61499) & ChrW(61474)
        .Font.NameOther = "EZ Psaltica"
        With .Replacement
            .Text = ChrW(61541) & ChrW(61498) & ChrW(61474)
            .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61541)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Spacing = -5
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61498)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Spacing = 5
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61474)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Scaling = 90
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

End Sub

Sub PolishNotes2()
'
' This is a continuation of the macro "PolishNotes1". These two macros are automatically run
'   by the macro "PolishNotes".
'

'
' The following 63 lines of code align a diesis beneath an elaphron
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61504) & "[" & ChrW(61565) & ChrW(61483) & "]"
        With .Replacement
        .Text = "^&"
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61483)
        .Font.Emboss = True
        .Font.NameOther = "EZ Psaltica"
       With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61504)
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = -5
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61565) & ChrW(61483) & "]"
        .Font.Emboss = True
        .Font.NameOther = "EZ Fthora"
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = 5
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 94 lines of code shift the aple and the antikenoma to the right when they are
'   beneath a petaste.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61553) & ChrW(61474) & ChrW(61499)
        .Font.NameOther = "EZ Psaltica"
        .Replacement.Text = ChrW(61553) & ChrW(61499) & ChrW(61474)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61553) & ChrW(61499) & ChrW(61474)
        .Font.NameOther = "EZ Psaltica"
        With .Replacement
            .Text = ChrW(61553) & ChrW(61498) & ChrW(61474)
            .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61553)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Spacing = -5
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61498)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Spacing = 5
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61474)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Scaling = 90
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 94 lines of code shift the aple and the antikenoma to the right when they are
'   beneath a petaste beneath an apostrophos.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61521) & ChrW(61474) & ChrW(61499)
        .Replacement.Text = ChrW(61521) & ChrW(61499) & ChrW(61474)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61521) & ChrW(61499) & ChrW(61474)
        With .Replacement
            .Text = ChrW(61521) & ChrW(61498) & ChrW(61474)
            .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61521)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Spacing = -5
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61498)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Spacing = 5
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61474)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Scaling = 90
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 94 lines of code shift the aple and the antikenoma to the right when they are
'   beneath a petaste beneath an ison.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61552) & ChrW(61474) & ChrW(61499)
        .Replacement.Text = ChrW(61552) & ChrW(61499) & ChrW(61474)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61552) & ChrW(61499) & ChrW(61474)
        With .Replacement
            .Text = ChrW(61552) & ChrW(61498) & ChrW(61474)
            .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61552)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Spacing = -5
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61498)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Spacing = 5
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61474)
        .Font.Emboss = True
        With .Replacement
            .Text = "^&"
            .Font.Emboss = False
            .Font.Scaling = 90
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 78 lines of code shift the klasma that is beneath a petaste in jumps of 4, 5, 6,
'   7, and 8
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61554) & ChrW(61562)
        .Replacement.Text = ChrW(61554) & ChrW(61585)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61556) & ChrW(61562)
        .Replacement.Text = ChrW(61556) & ChrW(61585)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61561) & ChrW(61562)
        .Replacement.Text = ChrW(61561) & ChrW(61585)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61557) & ChrW(61562)
        .Replacement.Text = ChrW(61557) & ChrW(61585)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61545) & ChrW(61562)
        .Replacement.Text = ChrW(61545) & ChrW(61585)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 144 lines of code lower the gorgon, digorgon, and trigorgon above an apostrophos
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61473) & ChrW(61508)
        With .Replacement
            .Text = "^&"
            .Font.Position = -3
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
'        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    ActiveWindow.ActivePane.VerticalPercentScrolled = 0
    
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61473) & ChrW(61515)
        With .Replacement
            .Text = "^&"
            .Font.Position = -3
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    ActiveWindow.ActivePane.VerticalPercentScrolled = 0
    
   Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61515)
       .Font.Position = -3
       .Font.NameOther = "EZ Psaltica"
        With .Replacement
            .Text = "^&"
            .Font.Position = 0
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61473) & ChrW(61510)
        With .Replacement
            .Text = "^&"
            .Font.Position = -3
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    ActiveWindow.ActivePane.VerticalPercentScrolled = 0
    

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61473) & ChrW(61512)
        With .Replacement
            .Text = "^&"
            .Font.Position = -3
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    ActiveWindow.ActivePane.VerticalPercentScrolled = 0
    
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61473) & ChrW(61507)
        With .Replacement
            .Text = "^&"
            .Font.Position = -3
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    ActiveWindow.ActivePane.VerticalPercentScrolled = 0
    

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61473) & ChrW(61526)
        With .Replacement
            .Text = "^&"
            .Font.Position = -3
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    ActiveWindow.ActivePane.VerticalPercentScrolled = 0
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61473)
        .Font.Position = -3
        With .Replacement
            .Text = "^&"
            .Font.Position = 0
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61511) & ChrW(61486)
        With .Replacement
            .Text = "^&"
            .Font.Position = 0
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 14 lines of code fix an orthographical error when the user puts a klasma beneath
'   a jump of four.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61492) & ChrW(61562)
        .Replacement.Text = ChrW(61492) & ChrW(61530)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 140 lines of text shift an omalon down when it collides with
'   a kentema or kentemata that are beneath an oligon.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61555) & ChrW(61531)
        .Replacement.Text = ChrW(61531) & ChrW(61555)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61540) & ChrW(61531)
        With .Replacement
        .Text = ChrW(61531) & ChrW(61540)
        .Font.NameOther = "EZ Psaltica"
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61542) & ChrW(61531)
        .Replacement.Text = ChrW(61531) & ChrW(61542)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61490) & ChrW(61646) & "]" & ChrW(61563)
        With .Replacement
             .Text = "^&"
             .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True

        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61490) & ChrW(61646) & "]"
        .Font.Emboss = True
        With .Replacement
             .Text = "^&"
             .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61490) & ChrW(61472) & ChrW(61488) & ChrW(61531)
        With .Replacement
             .Text = ChrW(61490) & ChrW(61488) & ChrW(61531)
             .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61490) & ChrW(61488) & ChrW(61531)
        With .Replacement
             .Text = "^&"
             .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61490) & ChrW(61488)
        .Font.Emboss = True
        With .Replacement
             .Text = "^&"
             .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61531)
        .Font.Emboss = True
        With .Replacement
             .Text = "^&"
             .Font.Emboss = False
             .Font.Position = -1
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61563)
        .Font.Emboss = True
        With .Replacement
             .Text = "^&"
             .Font.Emboss = False
             .Font.Position = -2
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 100 lines of code split an yporroe from the gorgon, digorgon and trigorgon.
'   (This is necessary so that an aple or diple beneath the yporroe will be properly aligned.)
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Psaltica"
        .Text = ChrW(61485)
        With .Replacement
        .Text = ChrW(61481) & ChrW(61648)
'        .Font.Engrave = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Special-I"
        .Text = ChrW(61535)
        With .Replacement
        .Text = ChrW(61511) & ChrW(61486)
'        .Font.Engrave = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Special-I"
        .Text = ChrW(61485)
        With .Replacement
        .Text = ChrW(61511) & ChrW(61543)
'        .Font.Engrave = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Special-I"
        .Text = ChrW(61563)
        With .Replacement
        .Text = ChrW(61511) & ChrW(61483)
'        .Font.Engrave = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Special-I"
        .Text = ChrW(61531)
        With .Replacement
        .Text = ChrW(61511) & ChrW(61502)
'        .Font.Engrave = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Special-I"
        .Text = ChrW(61533)
        With .Replacement
        .Text = ChrW(61511) & ChrW(61482)
'        .Font.Engrave = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 70 lines of code shift an omalon to the right when it is beneath an apostrophos
'  followed by an ison.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61473) & ChrW(61472) & ChrW(61488) & ChrW(61531)
        .Replacement.Text = ChrW(61473) & ChrW(61488) & ChrW(61531)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61473) & ChrW(61488) & ChrW(61531)
        With .Replacement
        .Text = ChrW(61473) & ChrW(61488) & ChrW(61563)
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61473)
        .Font.Emboss = True
        With .Replacement
        .Text = ChrW(61473)
        .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61488)
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = -14
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61563)
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = 14
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
'
' The following 67 lines of code raise the isokratema that is written above a gorgon
'   that is above kentemata that are above an oligon.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61548) & ChrW(61472) & "[" & ChrW(61528) & ChrW(61566) & _
             ChrW(61473) & ChrW(61507) & ChrW(61526) & ChrW(61506) & ChrW(61518) _
             & ChrW(61517) & ChrW(61500) & ChrW(61502) & ChrW(61503) & "]"
        With .Replacement
        .Text = "^&"
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61548) & "[" & ChrW(61528) & ChrW(61566) & _
             ChrW(61473) & ChrW(61507) & ChrW(61526) & ChrW(61506) & ChrW(61518) _
             & ChrW(61517) & ChrW(61500) & ChrW(61502) & ChrW(61503) & "]"
        With .Replacement
        .Text = "^&"
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61548) & ChrW(61472) & "]"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Special-II"
        .Text = "[" & ChrW(61528) & ChrW(61566) & _
             ChrW(61473) & ChrW(61507) & ChrW(61526) & ChrW(61506) & ChrW(61518) _
             & ChrW(61517) & ChrW(61500) & ChrW(61502) & ChrW(61503) & "]"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Position = 2
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61528) & ChrW(61566) & _
             ChrW(61473) & ChrW(61507) & ChrW(61526) & ChrW(61506) & ChrW(61518) _
             & ChrW(61517) & ChrW(61500) & ChrW(61502) & ChrW(61503) & "]"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

End Sub

Sub PolishNotes2b()
'
' The following 46 lines of code shift a gorgon to its proper position when placed
' on an oligon that has an ypsele and kentemata above it (a jump of 4+1)
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61557) & ChrW(61555)
        With .Replacement
        .Text = "^&"
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61557)
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = -4
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61555)
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = 4
        .Font.Position = 4
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
'
' The following 81 lines of code align and stretch a psefiston that is beneath a "long" oligon.
' A "long" oligon is created by the characters in Psaltica: R, T, Y, and P
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61522) & ChrW(61524) & ChrW(61529) & ChrW(61520) & _
             "]" & ChrW(61479)
        With .Replacement
        .Font.Emboss = True
        .Text = "^&"
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.Emboss = True
        .Text = "[" & ChrW(61522) & ChrW(61524) & ChrW(61529) & ChrW(61520) & _
             "]"
        With .Replacement
        .Font.Emboss = False
        .Text = "^&"
        .Font.Spacing = -3
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61479)
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = 3
        .Font.Scaling = 125
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True

        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
'
' The following 76 lines of code raise a klasma that is above an elaphron
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61504) & ChrW(61505)
        .Font.NameOther = "EZ Psaltica"
        .Replacement.Text = ChrW(61504) & ChrW(61537)
        .Forward = True
        .Wrap = wdFindContinue
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61535) & ChrW(61505)
        .Font.NameOther = "EZ Psaltica"
        .Replacement.Text = ChrW(61535) & ChrW(61537)
        .Forward = True
        .Wrap = wdFindContinue
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61475) & ChrW(61505)
        .Font.NameOther = "EZ Psaltica"
        .Replacement.Text = ChrW(61475) & ChrW(61537)
        .Forward = True
        .Wrap = wdFindContinue
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61475) & ChrW(61504) & ChrW(61535) & "]" & ChrW(61537)
        .Font.NameOther = "EZ Psaltica"
        With .Replacement
        .Text = "^&"
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61475) & ChrW(61504) & ChrW(61535) & "]"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61537)
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Position = 1
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
'
' The following 100 lines of code add space after an yporroe that has
' a gorgon, digorgon, or trigorgon above it, regardless if there is an
' aple or diple beneath them.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
         .Text = "[" & ChrW(61543) & ChrW(61486) & ChrW(61502) & _
             ChrW(61483) & "][" & ChrW(61498) & ChrW(61515) & "]"
        With .Replacement
        .Text = "^&"
        .Font.Spacing = 5
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61648) & ChrW(61482) & "][" & _
              ChrW(61498) & ChrW(61515) & "]"
        With .Replacement
        .Text = "^&"
        .Font.Spacing = 3
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61648) & ChrW(61543) & ChrW(61486) & ChrW(61502) & _
             ChrW(61483) & ChrW(61482) & "]"
        With .Replacement
        .Text = "^&"
        .Font.Spacing = 0
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61481) & ChrW(61511) & "][" & ChrW(61648) & ChrW(61543) & ChrW(61486) & ChrW(61502) & _
             ChrW(61483) & ChrW(61482) & "][!" & ChrW(61498) & ChrW(61515) & "]"
        With .Replacement
        .Text = "^&"
        .Font.Spacing = 5
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[!" & ChrW(61648) & ChrW(61543) & ChrW(61486) & ChrW(61502) & _
             ChrW(61483) & ChrW(61482) & "]"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Spacing = 0
        .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61648) & ChrW(61482) & "]"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Spacing = 3
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.WholeStory
    Selection.Font.Emboss = False
    
'
' The following 46 lines of code fix a psefiston that colides with
'  kentemata that are beneath an oxeia.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Oxeia"
        .Text = ChrW(61551) & ChrW(61479)
        With .Replacement
        .Text = ChrW(61646) & ChrW(61479)
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Oxeia"
        .Text = ChrW(61646)
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = 4
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Oxeia"
        .Text = ChrW(61479)
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 10 lines of code shrink the kentemata beneath an oxeia
'  when they are too close to an omalon beneath them.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Oxeia"
        .Text = ChrW(61551) & ChrW(61563)
        .Replacement.Text = ChrW(61646) & ChrW(61563)
        .Forward = True
        .Wrap = wdFindContinue
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
'
' The following 15 lines of code replace two bar lines in a row
'  with a single character that has those two bar lines closer together.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61514) & ChrW(61514)
        .Font.NameOther = "EZ Psaltica"
        With .Replacement
        .Text = ChrW(61472) & ChrW(61472) & ChrW(61472) & ChrW(61557) & ChrW( _
            61472) & ChrW(61472) & ChrW(61472) & ChrW(61472) & ChrW(61472)
        .Font.NameOther = "EZ Oxeia"
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 52 lines of code align a psefiston with an oxeia that is
'  beneath kentemata that have an elaphron or an ison to the left of them
'  that are also above the oxeia.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61524) & ChrW(61529) & ChrW(61520) & ChrW( _
            61535) & "]" & ChrW(61479)
        .Font.NameOther = "EZ Oxeia"
        With .Replacement
        .Text = "^&"
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61524) & ChrW(61529) & ChrW(61520) & ChrW( _
             61535) & "]"
        .Font.NameOther = "EZ Oxeia"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = -2
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61479)
        .Font.NameOther = "EZ Oxeia"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = 2
        .Font.Scaling = 125
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 16 lines of code shift the gorgon to the right when it is
'   above kentemata that are above an oxeia and to the right of a hamele,
'   elaphron, or ison.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61522) & ChrW(61524) & ChrW(61520) & "]" & ChrW( _
            61523)
        .Font.NameOther = "EZ Oxeia"
        With .Replacement
        .Text = "^&"
        .Font.Spacing = 0
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 92 lines of code align a parestigmeno gorgon that is above
'   kentemata that are above an oxeia.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61522) & ChrW(61524) & ChrW(61520) & ChrW(61529) & _
             ChrW(61525) & "]"
        .Font.NameOther = "EZ Oxeia"
        With .Replacement
        .Text = "^&"
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61512)
        .Font.NameOther = "EZ Special-I"
        With .Replacement
        .Text = "^&"
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61522) & ChrW(61524) & ChrW(61520) & ChrW(61529) & _
             ChrW(61525) & "]" & ChrW(61512)
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Engrave = True
        .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61522) & ChrW(61524) & ChrW(61520) & "]"
        .Font.NameOther = "EZ Oxeia"
        .Font.Engrave = True
        With .Replacement
        .Text = "^&"
        .Font.Engrave = False
        .Font.Spacing = 0
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61512)
        .Font.NameOther = "EZ Special-I"
        .Font.Engrave = True
        With .Replacement
        .Text = "^&"
        .Font.Engrave = False
        .Font.Spacing = -4
        .Font.Position = 3
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.WholeStory
    With Selection.Font
        .Emboss = False
        .Engrave = False
    End With

'
' The following 10 lines of code shift a gorgon to the right
'  when placed beneath an oxeia.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61489) & ChrW(61560)
        .Font.NameOther = "EZ Oxeia"
        .Replacement.Text = ChrW(61489) & ChrW(61559)
        .Forward = True
        .Wrap = wdFindContinue
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 58 lines of code reposition an aple that is beneath an antikenoma,
'  beneath a kentema beneath an oxeia.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61490) & ChrW(61474) & ChrW(61498)
        .Font.NameOther = "EZ Oxeia"
        .Replacement.Text = ChrW(61501) & ChrW(61499)
        .Forward = True
        .Wrap = wdFindContinue
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61501) & ChrW(61499)
        .Font.NameOther = "EZ Oxeia"
        With .Replacement
        .Text = "^&"
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61501)
        .Font.NameOther = "EZ Oxeia"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61499)
        .Font.NameOther = "EZ Oxeia"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Position = -4
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 79 lines of code reposition an aple that is beneath an antikenoma,
'  beneath kentemata beneath an oxeia.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61551) & ChrW(61474) & ChrW(61498)
        .Font.NameOther = "EZ Oxeia"
        .Replacement.Text = ChrW(61551) & ChrW(61498) & ChrW(61474)
        .Forward = True
        .Wrap = wdFindContinue
        .MatchWildcards = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61551) & ChrW(61498) & ChrW(61474)
        .Font.NameOther = "EZ Oxeia"
        With .Replacement
        .Text = "^&"
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61551)
        .Font.NameOther = "EZ Oxeia"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = -6
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61498)
        .Font.NameOther = "EZ Oxeia"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Position = -3
        .Font.Spacing = 2
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61474)
        .Font.NameOther = "EZ Oxeia"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Position = -3
        .Font.Spacing = 4
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
'  BEGINNING OF FAULTY CODE (It has been omitted, because this code creates
'    errors for users who don't insert spaces between qualitative symbols
'    when they type in the music.)
'
' The following 57 lines of code shift the isokratema slightly
'  to the left when it is above a character of medium width,
'  such as the petaste, elaphron, etc.
'
'Selection.Find.ClearFormatting
'    Selection.Find.Replacement.ClearFormatting
'    With Selection.Find
'        .Text = "[" & ChrW(61504) & ChrW(61535) & ChrW(61475) & ChrW(61521) & _
'             ChrW(61527) & ChrW(61509) & ChrW(61553) & ChrW(61559) & ChrW(61541) _
'             & ChrW(61552) & "][" & ChrW(61536) & ChrW(61489) & _
'            ChrW(61539) & ChrW(61558) & ChrW(61538) & ChrW(61550) & ChrW(61549) _
'            & ChrW(61484) & ChrW(61486) & ChrW(61487) & "]"
'        With .Replacement
'        .Text = "^&"
'        .Font.Emboss = True
'        End With
'        .Forward = True
'        .Wrap = wdFindContinue
'        .Format = True
'        .MatchCase = False
'        .MatchWildcards = True
'    End With
'    Selection.Find.Execute Replace:=wdReplaceAll
'
'    Selection.Find.ClearFormatting
'    Selection.Find.Replacement.ClearFormatting
'    With Selection.Find
'        .Text = "[" & ChrW(61504) & ChrW(61535) & ChrW(61521) & ChrW(61527) & _
'             ChrW(61509) & ChrW(61553) & ChrW(61559) & ChrW(61541) & ChrW(61552) _
'             & ChrW(61475) & "]"
'        .Font.Emboss = True
'        With .Replacement
'        .Text = "^&"
'        .Font.Emboss = False
'        .Font.Spacing = -4
'        End With
'        .Forward = True
'        .Wrap = wdFindContinue
'        .Format = True
'        .MatchWildcards = True
'    End With
'    Selection.Find.Execute Replace:=wdReplaceAll
'
'    Selection.Find.ClearFormatting
'    Selection.Find.Replacement.ClearFormatting
'    With Selection.Find
'        .Text = "[" & ChrW(61536) & ChrW(61489) & ChrW(61539) & _
'            ChrW(61558) & ChrW(61538) & ChrW(61550) & ChrW(61549) & ChrW(61484) _
'            & ChrW(61486) & ChrW(61487) & "]"
'        .Font.Emboss = True
'        With .Replacement
'        .Text = "^&"
'        .Font.Emboss = False
'        .Font.Spacing = 4
'        End With
'        .Forward = True
'        .Wrap = wdFindContinue
'        .Format = True
'        .MatchWildcards = True
'    End With
'    Selection.Find.Execute Replace:=wdReplaceAll
'
'  END OF FAULTY CODE

'
' The following 15 lines of code expand the spacing of an
'  apostrophos immediately followed by a blank space
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61473) & ChrW(61472)
        With .Replacement
        .Text = "^&"
        .Font.Spacing = 1
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 43 lines of code expand the spacing after an
'  apostrophos followed by a gorgon and a space.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61473) & ChrW(61523) & ChrW(61472)
        With .Replacement
        .Text = "^&"
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61473)
        .Font.Emboss = True
       With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61523) & ChrW(61472)
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = 1
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' These next 15 lines of code set the vertical height of all
'  fthores to zero (since some macros accidentally lowered them)
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "^?"
        .Font.NameOther = "EZ Fthora"
        With .Replacement
        .Text = "^&"
        .Font.Position = 0
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 106 lines of code raise the ison when preceded by a number 3 or 4
'   so that they don't collide
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61492) & "[" & ChrW(61517) & ChrW(61528) & ChrW(61507) & _
             ChrW(61526) & ChrW(61506) & ChrW(61518) & ChrW(61500) & ChrW(61502) _
             & ChrW(61503) & "]"
        .Font.NameOther = "EZ Special-II"
        With .Replacement
        .Font.Emboss = True
        .Text = "^&"
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61492)
        .Font.Emboss = True
        With .Replacement
        .Font.Emboss = False
        .Font.Position = -1
        .Text = "^&"
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61517) & ChrW(61528) & ChrW(61507) & _
             ChrW(61526) & ChrW(61506) & ChrW(61518) & ChrW(61500) & ChrW(61502) _
             & ChrW(61503) & "]"
        .Font.Emboss = True
        With .Replacement
        .Font.Emboss = False
        .Font.Position = 1
        .Text = "^&"
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61491) & "[" & ChrW(61517) & ChrW(61528) & ChrW(61507) & _
             ChrW(61526) & ChrW(61506) & ChrW(61518) & ChrW(61500) & ChrW(61502) _
             & ChrW(61503) & "]"
        .Font.NameOther = "EZ Special-II"
        With .Replacement
        .Font.Emboss = True
        .Text = "^&"
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61491)
        .Font.Emboss = True
        With .Replacement
        .Font.Emboss = False
        .Font.Position = -1
        .Text = "^&"
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61517) & ChrW(61528) & ChrW(61507) & _
             ChrW(61526) & ChrW(61506) & ChrW(61518) & ChrW(61500) & ChrW(61502) _
             & ChrW(61503) & "]"
        .Font.Emboss = True
        With .Replacement
        .Font.Emboss = False
        .Font.Position = 1
        .Text = "^&"
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 49 lines of code shift the numbers 3 and 4 to the left
'  when they collide with the kentema above an oligon (in jumps of 3)
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61491) & "[" & ChrW(61491) & ChrW(61492) & "]"
        With .Replacement
        .Font.Emboss = True
        .Text = "^&"
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61491)
        .Font.Emboss = True
        .Font.NameOther = "EZ Psaltica"
        With .Replacement
        .Font.Emboss = False
        .Font.Spacing = -2
        .Text = "^&"
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "[" & ChrW(61491) & ChrW(61492) & "]"
        .Font.Emboss = True
        .Font.NameOther = "EZ Special-II"
        With .Replacement
        .Font.Emboss = False
        .Font.Spacing = 2
        .Text = "^&"
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 58 lines of code shift a dotted gorgon to the left so
'  that it is aligned above kentemata that are above an oligon.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61519) & ChrW(61512)
        With .Replacement
        .Text = "^&"
        .Font.Shadow = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
        .MatchWholeWord = False
        .MatchWildcards = False
        .MatchSoundsLike = False
        .MatchAllWordForms = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61512)
        .Font.Shadow = True
        With .Replacement
        .Text = ChrW(61544)
        .Font.Shadow = False
        .Font.Position = 3
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
        .MatchWholeWord = False
        .MatchWildcards = False
        .MatchSoundsLike = False
        .MatchAllWordForms = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61519)
        .Font.Shadow = True
        With .Replacement
        .Text = ChrW(61655)
        .Font.Shadow = False
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
        .MatchWholeWord = False
        .MatchWildcards = False
        .MatchSoundsLike = False
        .MatchAllWordForms = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll


End Sub

'
'
'
'
'
'
'
'
'
'
'
'
'
'

Sub MakeNotesRed()
'
' MakeNotesRed Macro
' This macro makes all the appropriate notes red. In particular it changes every instance of the
'     gorgon, digorgon, trigorgon, fthores, elxeis, tempo marks, martyries, isokratema,
'     and all the older Byzantine music symbols, such as the isaki, tromikon, lygisma, etc.
'
' The following 90 lines of code make all the aforementioned characters red, except for the
'     gorgon, the digorgon, and the trigorgon.
'
    Selection.HomeKey Unit:=wdStory

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Special-II"
        .Text = "[" & ChrW(61539) & ChrW(61558) & _
             ChrW(61538) & ChrW(61550) & ChrW(61549) & ChrW(61484) & ChrW(61486) _
             & ChrW(61487) & ChrW(61507) & ChrW(61526) & ChrW(61506) & ChrW( _
            61518) & ChrW(61517) & ChrW(61500) & ChrW(61502) & ChrW(61503) & _
            ChrW(61483) & ChrW(61530) & ChrW(61501) & ChrW(61560) _
            & ChrW(61532) & ChrW(61622) & "]"
        With .Replacement
            .Text = "^&"
            .Font.Color = 237
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True


        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Special-I"
        .Text = "[" & ChrW(61505) & ChrW(61537) & ChrW(61523) & ChrW(61555) & _
             ChrW(61530) & ChrW(61562) & ChrW(61528) & ChrW(61560) & ChrW(61550) _
             & ChrW(61549) & ChrW(61484) & ChrW(61487) & ChrW(61479) & ChrW(61474) & ChrW( _
            61518) & ChrW(61517) & ChrW(61500) & ChrW(61503) & _
            ChrW(61566) & "]"
        With .Replacement
            .Text = "^&"
            .Font.Color = 237
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Psaltica"
        .Text = "[" & ChrW(61539) & ChrW(61558) & ChrW(61538) & ChrW(61550) & _
             ChrW(61549) & ChrW(61484) & ChrW(61486) & ChrW(61487) & ChrW(61507) _
             & ChrW(61526) & ChrW(61506) & ChrW(61518) & ChrW(61517) & ChrW( _
            61500) & ChrW(61502) & ChrW(61503) & ChrW(61533) & ChrW( _
            61514) & ChrW(61546) & ChrW(61609) & "]"
        With .Replacement
            .Text = "^&"
            .Font.Color = 237
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Oxeia"
        .Text = "[" & ChrW(61559) & ChrW(61555) & ChrW(61523) & ChrW(61560) & _
             ChrW(61528) & ChrW(61539) & ChrW(61558) & ChrW(61538) & ChrW(61484) _
             & ChrW(61486) & ChrW(61554) & ChrW(61556) & ChrW(61561) & ChrW( _
            61557) & ChrW(61564) & ChrW(61503) & ChrW(61533) & _
            ChrW(61565) & ChrW(61541) & ChrW(61609) & "]"
        With .Replacement
            .Text = "^&"
            .Font.Color = 237
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
   
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Fthora"
        .Text = "?"
        With .Replacement
            .Text = "^&"
            .Font.Color = 237
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll


' The following 201 lines of code split compound characters containing a gorgon, digorgon, or a
'    trigorgon into two separate characters, so that the gorgon part of it can later be made red.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Psaltica"
        .Text = ChrW(61548)
        .Replacement.Text = ChrW(61655) & ChrW(61688)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Psaltica"
        .Text = ChrW(61516)
        .Replacement.Text = ChrW(61655) & ChrW(61668)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Special-I"
        .Text = ChrW(61493)
        .Replacement.Text = ChrW(61556) & ChrW(61536)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Special-I"
        .Text = ChrW(61524)
        .Replacement.Text = ChrW(61556) & ChrW(61564)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Special-I"
        .Text = ChrW(61496)
        .Replacement.Text = ChrW(61556) & ChrW(61476)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Special-I"
        .Text = ChrW(61494)
        .Replacement.Text = ChrW(61556) & ChrW(61475)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 49 lines of code split a gorgon with an aple to the right
'  of it from the oligon and kentemata they are with.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61495)
        .Font.NameOther = "EZ Special-I"
        With .Replacement
        .Text = ChrW(61556) & ChrW(61512)
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61556)
        .Font.NameOther = "EZ Special-I"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = -15
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll


    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61512)
        .Font.NameOther = "EZ Special-I"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = 15
        .Font.Position = 1
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 48 lines of code split a digorgon with an aple to the left
'  of it from the oligon and kentemata they are with.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61497)
        .Font.NameOther = "EZ Special-I"
        With .Replacement
        .Text = ChrW(61556) & ChrW(61508)
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61556)
        .Font.NameOther = "EZ Special-I"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = -16
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll


    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61508)
        .Font.NameOther = "EZ Special-I"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = 16
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 48 lines of code split a trigorgon with an aple to the left
'  of it from the oligon and kentemata they are with.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61529)
        .Font.NameOther = "EZ Special-I"
        With .Replacement
        .Text = ChrW(61556) & ChrW(61510)
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61556)
        .Font.NameOther = "EZ Special-I"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = -18
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll


    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61510)
        .Font.NameOther = "EZ Special-I"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = 18
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 48 lines of code split a trigorgon with an aple to the right
'  of it from the oligon and kentemata they are with.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61525)
        .Font.NameOther = "EZ Special-I"
        With .Replacement
        .Text = ChrW(61556) & ChrW(61526)
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61556)
        .Font.NameOther = "EZ Special-I"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = -18
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll


    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61526)
        .Font.NameOther = "EZ Special-I"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = 18
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 48 lines of code split a trigorgon with an aple to the right
'  of it from the oligon and kentemata they are with.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61513)
        .Font.NameOther = "EZ Special-I"
        With .Replacement
        .Text = ChrW(61556) & ChrW(61507)
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61556)
        .Font.NameOther = "EZ Special-I"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = -17
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll


    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61507)
        .Font.NameOther = "EZ Special-I"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = 17
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 10 lines of code split a gorgon with an aple to the right
' of it from an yporroe.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61565)
        .Font.NameOther = "EZ Special-I"
        .Replacement.Text = ChrW(61511) & ChrW(61626)
        .Forward = True
        .Wrap = wdFindContinue
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 382 lines of code split the characters in the Oxeia font that
'  have gorgons into two separate characters so that only the gorgon (or
'  digorgon or trigorgon) can be made red without making the rest of the
'  character red.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61548)
        .Font.NameOther = "EZ Oxeia"
        With .Replacement
        .Text = ChrW(61655) & ChrW(61555)
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61655)
        .Font.NameOther = "EZ Oxeia"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = -1
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61555)
        .Font.NameOther = "EZ Oxeia"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = 1
        .Font.Position = 3
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
'
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61482)
        .Font.NameOther = "EZ Oxeia"
        With .Replacement
        .Text = ChrW(61478) & ChrW(61555)
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61478)
        .Font.NameOther = "EZ Oxeia"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = -8
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61555)
        .Font.NameOther = "EZ Oxeia"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = 8
        .Font.Position = 5
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
'
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61480)
        .Font.NameOther = "EZ Oxeia"
        With .Replacement
        .Text = ChrW(61478) & ChrW(61540)
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61478)
        .Font.NameOther = "EZ Oxeia"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = -9
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61540)
        .Font.NameOther = "EZ Oxeia"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = 9
        .Font.Position = 5
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
'
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61485)
        .Font.NameOther = "EZ Oxeia"
        With .Replacement
        .Text = ChrW(61536) & ChrW(61555)
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61536)
        .Font.NameOther = "EZ Oxeia"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = -1
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61555)
        .Font.NameOther = "EZ Oxeia"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = 1
        .Font.Position = 5
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
'
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61514)
        .Font.NameOther = "EZ Oxeia"
        With .Replacement
        .Text = ChrW(61478) & ChrW(61542)
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61478)
        .Font.NameOther = "EZ Oxeia"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = -12
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61542)
        .Font.NameOther = "EZ Oxeia"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = 12
        .Font.Position = 5
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
'
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61546)
        .Font.NameOther = "EZ Oxeia"
        With .Replacement
        .Text = ChrW(61478) & ChrW(61540)
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61478)
        .Font.NameOther = "EZ Oxeia"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = -11
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61540)
        .Font.NameOther = "EZ Oxeia"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = 11
        .Font.Position = 5
        .Font.NameOther = "EZ Special-I"
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
'
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61626)
        .Font.NameOther = "EZ Oxeia"
        With .Replacement
        .Text = ChrW(61478) & ChrW(61542)
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61478)
        .Font.NameOther = "EZ Oxeia"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = -13
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61542)
        .Font.NameOther = "EZ Oxeia"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = 13
        .Font.Position = 5
        .Font.NameOther = "EZ Special-I"
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
'
' The following 48 lines of code split a trigorgon from an oxeia with
'  kentemata above them.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61516)
        .Font.NameOther = "EZ Oxeia"
        With .Replacement
        .Text = ChrW(61655) & ChrW(61508)
        .Font.Emboss = True
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61655)
        .Font.NameOther = "EZ Oxeia"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = -8
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll


    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = ChrW(61508)
        .Font.NameOther = "EZ Oxeia"
        .Font.Emboss = True
        With .Replacement
        .Text = "^&"
        .Font.Emboss = False
        .Font.Spacing = 8
        .Font.Position = -1
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

'
' The following 86 lines of code make all gorgons, digorgons, and trigorgons red.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Psaltica"
        .Text = "[" & ChrW(61523) & ChrW(61555) & _
             ChrW(61508) & ChrW(61540) & ChrW(61510) & ChrW(61542) & ChrW(61511) _
             & ChrW(61543) & ChrW(61512) & ChrW(61544) & ChrW(61528) & ChrW( _
            61560) & ChrW(61648) & ChrW(61688) & ChrW(61668) & "]"
        With .Replacement
            .Text = "^&"
            .Font.Color = 237
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Special-I"
        .Text = "[" & ChrW(61508) & ChrW(61540) & ChrW(61510) & ChrW(61542) & _
             ChrW(61512) & ChrW(61544) & ChrW(61514) & ChrW(61515) & ChrW(61547) _
             & ChrW(61516) & ChrW(61548) & ChrW(61539) & ChrW(61558) & ChrW( _
            61538) & ChrW(61507) & ChrW(61526) & ChrW(61506) & ChrW(61543) & _
            ChrW(61483) & ChrW(61486) & ChrW(61502) & ChrW(61482) & ChrW(61564) _
            & ChrW(61476) & ChrW(61475) & ChrW(61536) & ChrW(61626) & "]"
        With .Replacement
            .Text = "^&"
            .Font.Color = 237
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Special-I"
        .Text = ChrW(61514)
        With .Replacement
            .Text = "^&"
            .Font.Color = 237
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
  
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Special-II"
       .Text = "[" & ChrW(61473) & ChrW(61489) & ChrW(61536) & ChrW(61566) & _
             "]"
        With .Replacement
            .Text = "^&"
            .Font.Color = 237
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
  
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Oxeia"
        .Text = "[" & ChrW(61555) & ChrW(61540) & ChrW(61542) & ChrW(61508) & _
             ChrW(61510) & ChrW(61511) & ChrW(61543) & "]"
        With .Replacement
            .Text = "^&"
            .Font.Color = 237
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

End Sub

'
'
'
'
'
'
'
'
'
'
'
Sub ExpandLine()
'
' ExpandLine Macro
' Macro recorded 2/2/2005 by Father Ephraim
'
' Each time the following little macro is run, it will increase the font size of every small
'  character in the line of text where the cursor is by a half point. This is useful after
'  running the "Justify" macro for a file with Byzantine notation, because the "Justify"
'  macro increases the spacing between notes on all the lines except for the last
'  line. By running this macro once or twice on that last line, you can make its spacing
'  look similar to that of the other lines. This macro is also useful for increasing the
'  spacing on lines that have syllables with many letters associated with notes that
'  do not take up a lot of space horizontally.
'
Dim y
    
    Selection.HomeKey Unit:=wdLine
    Selection.EndKey Unit:=wdLine, Extend:=wdExtend

    For Each y In Selection.Characters
        If y.Font.Size < 10 Then
            y.Font.Size = y.Font.Size + 0.5
        End If
    Next
End Sub
'
'
'
'
'
'
'
Sub CompressLine()
' CompressLine Macro
' Macro recorded 2/2/2005 by Father Ephraim
'
' This little macro undoes what the "ExpandLine" macro does. In other words, it shrinks by a half
'   point every blank space which had been expanded by that macro.
'
Dim y
    
    Selection.HomeKey Unit:=wdLine
    Selection.EndKey Unit:=wdLine, Extend:=wdExtend

    For Each y In Selection.Characters
        If y.Font.Size < 11 And y.Font.Size > 1 Then
            y.Font.Size = y.Font.Size - 0.5
        End If
    Next
End Sub

'
'
'
'
'

Sub MakeIsonBlue()
'
' MakeIsonBlue Macro
' Macro recorded 3/25/2005 by Father Ephraim
'
' This little macro makes all isokratema symbols blue.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Special-II"
        .Text = "[" & ChrW(61539) & ChrW(61507) & ChrW(61558) & ChrW(61526) & _
             ChrW(61538) & ChrW(61506) & ChrW(61550) & ChrW(61518) & ChrW(61549) _
             & ChrW(61517) & ChrW(61484) & ChrW(61500) & ChrW(61486) & ChrW( _
            61502) & ChrW(61487) & ChrW(61503) & ChrW(61536) & ChrW(61566) & _
            ChrW(61489) & ChrW(61473) & ChrW(61530) & ChrW(61560) & ChrW(61622) & "]"
        With .Replacement
        .Text = "^&"
        .Font.Color = 16729600
'        .Font.Color = wdColorBlue
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = False
        .MatchWholeWord = False
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
End Sub

'
'
'
'
'

Sub MakeIsonGreen()
'
' MakeIsonGreen Macro
' Macro recorded 3/25/2005 by Father Ephraim
'
' This little macro makes all isokratema symbols green.
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Font.NameOther = "EZ Special-II"
        .Text = "[" & ChrW(61539) & ChrW(61507) & ChrW(61558) & ChrW(61526) & _
             ChrW(61538) & ChrW(61506) & ChrW(61550) & ChrW(61518) & ChrW(61549) _
             & ChrW(61517) & ChrW(61484) & ChrW(61500) & ChrW(61486) & ChrW( _
            61502) & ChrW(61487) & ChrW(61503) & ChrW(61536) & ChrW(61566) & _
            ChrW(61489) & ChrW(61473) & ChrW(61530) & ChrW(61560) & ChrW(61622) & "]"
        With .Replacement
        .Text = "^&"
        .Font.Color = wdColorGreen
        End With
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchCase = False
        .MatchWholeWord = False
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
End Sub


Sub FormatTextBox()
'
' textbox Macro
' Macro recorded 9/3/2006 by Stefanos Souldatos
'
    
    Selection.Font.Name = "EZ Omega"
    Selection.Font.Size = 12
    
    With Selection.ParagraphFormat
        .LeftIndent = InchesToPoints(0)
        .RightIndent = InchesToPoints(0)
        .SpaceBefore = 0
        .SpaceBeforeAuto = False
        .SpaceAfter = 0
        .SpaceAfterAuto = False
        .LineSpacingRule = wdLineSpaceExactly
        .LineSpacing = 60
        .Alignment = wdAlignParagraphLeft
        .WidowControl = True
        .KeepWithNext = False
        .KeepTogether = False
        .PageBreakBefore = False
        .NoLineNumber = False
        .Hyphenation = True
        .FirstLineIndent = InchesToPoints(0)
        .OutlineLevel = wdOutlineLevelBodyText
        .CharacterUnitLeftIndent = 0
        .CharacterUnitRightIndent = 0
        .CharacterUnitFirstLineIndent = 0
        .LineUnitBefore = 0
        .LineUnitAfter = 0
    End With
    
    Selection.WholeStory
    
    With Selection.ShapeRange
        .Fill.Visible = False 'msoFalse
        .Line.Visible = msoFalse
        .LockAspectRatio = msoFalse
        
        .TextFrame.MarginLeft = 0#
        .TextFrame.MarginRight = 0#
        .TextFrame.MarginTop = 0#
        .TextFrame.MarginBottom = 0#
        
        .RelativeHorizontalPosition = wdRelativeHorizontalPositionColumn
        .RelativeVerticalPosition = wdRelativeVerticalPositionParagraph
        .Top = CentimetersToPoints(0.2)
        .Height = 680
        .Width = 470
        .Left = -5
        
        .LockAnchor = False
        .WrapFormat.AllowOverlap = True
        .WrapFormat.Side = wdWrapBoth
        .WrapFormat.DistanceTop = CentimetersToPoints(0)
        .WrapFormat.DistanceBottom = CentimetersToPoints(0)
        .WrapFormat.DistanceLeft = CentimetersToPoints(0) '(0.32)
        .WrapFormat.DistanceRight = CentimetersToPoints(0) '(0.32)
        .WrapFormat.Type = 3
        
        .ZOrder 4
        .TextFrame.AutoSize = False
        .TextFrame.WordWrap = True
    End With
        
End Sub
+----------+--------------------+---------------------------------------------+
|Type      |Keyword             |Description                                  |
+----------+--------------------+---------------------------------------------+
|Suspicious|run                 |May run an executable file or a system       |
|          |                    |command                                      |
|Suspicious|ChrW                |May attempt to obfuscate specific strings    |
|          |                    |(use option --deobf to deobfuscate)          |
|Suspicious|Hex Strings         |Hex-encoded strings were detected, may be    |
|          |                    |used to obfuscate strings (option --decode to|
|          |                    |see all)                                     |
|Suspicious|Base64 Strings      |Base64-encoded strings were detected, may be |
|          |                    |used to obfuscate strings (option --decode to|
|          |                    |see all)                                     |
+----------+--------------------+---------------------------------------------+

