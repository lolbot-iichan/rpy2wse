#rpy2wse
Converts Ren'Py visual novels to WebStory Engine HTML5 game using RPYC and some code magic

##CONTACTS
Copyleft by lolbot, member of IIchan.hk eroge project.
Written on hard day's nights of pretty nice autumn 2013.
You can mail me at: lolbot_iichan@mail.ru

##NO GUARANTIES
* Please, note, that this code is not perfect.
* IN FACT, THERE ARE ABSULUTELY NO GUARANTIES.
* Some problems must be marked by converter with "<!-- [TODO] -->" comments in generated xml file.
* However, even if there is no such comments, converted code still may be wrong in some way.
* Python is not my native language, so sorry for awful non-pythonic style.

##LICENSE? WHAT LICENSE?
It's mostly a Proof Of Concept. You can use this code however you want, I think. But be warned, you won't get any presents from Santa, if you delete all the copylefts and introduce this work as your's.


##CHANGELOG

###0.1 - 2013.10.11
+ renpy.ast.Say: simple text by defined characters
+ renpy.ast.UserStatement: play, stop
+ renpy.ast.Translate
+ renpy.ast.EndTranslate
+ renpy.ast.Menu: each block is one jump command
+ renpy.ast.Jump: no expressions
+ renpy.ast.Return
+ renpy.ast.Scene
+ renpy.ast.Show
+ renpy.ast.Hide
+ Runtime: simple menu, jump to rpy_start

###0.2 - 2013.10.20
+ renpy.ast.With: None, Fade, Dissolve
+ Styles: main menu background
+ Runtime: calling splashscreen, if present
+ Useless: Debug file added

###0.3 - 2013.10.27
+ convert mp3 to ogg and back (using console utils)
+ renpy.ast.Python: simple math only (aka 'x = True', 'x = x + 9', 'x += 1')
+ renpy.ast.If: simple conditions only (aka 'if x', 'if False', 'else')
+ renpy.ast.Menu: blocks inside branches
+ renpy.ast.Python: renpy.pause calls
+ renpy.ast.UserStatement: pause
+ renpy.ast.With: Pause

###0.4 - 2014.08.12
+ Styles: config.main_menu_music
+ Styles: config.window_icon
+ Runtime: hide&show textbox during transitions
+ renpy.ast.Say: {{, \n, {i}, {b}, {u}, {s}
+ renpy.ast.Pass
+ renpy.ast.Python: string assignment     (aka 'x = "qwerty"')
+ renpy.ast.If: more simple conditions    (aka 'if x == 0', 'if x == "qwerty"')
+ renpy.ast.Call: no expressions
+ renpy.ast.With: vpunch, hpunch          (aka 'with vpunch')
+ renpy.display.motion.ATLTransform       (aka 'show slavya at right')

###0.5 - in progress
+ Runtime: toggle textbox on 'h'
+ Runtime: simple help screen
+ Runtime: toggle savegames menu on Right-click
+ Styles: config.main_menu_music
+ renpy.ast.With: MoveTransition (aka 'show slavya at right with move', using <move asset="my_image" duration="1000" />)

##THINGS TO DO IN NEAREST FUTURE

###using &lt;var/&gt;:
+ renpy.ast.Python: more complex math (aka 'x = y * 3 + 2')
+ renpy.ast.If: refactoring for using nested tags
+ renpy.ast.Menu: refactoring for using nested tags
+ renpy.ast.If: more complex math  (aka 'if x == 2', 'if x > 5 and x < y')
+ renpy.ast.Menu: options with conditions
+ renpy.ast.Jump: expression
+ renpy.ast.Call: expression

###runtime:
+ Runtime: toggle fullscreen on 'f'
+ Runtime: toggle fastforward on 'tab'
+ Runtime: fastforward during 'ctrl'
+ Runtime: toggle textbox on Middle-click

###conversion:
+ Convertion: download audio conversion tools
+ Convertion: patch RenPy's script.py file

###styles:
+ Styles: generate hardcoded styles.css
+ Styles: generate styles for default font and text size
+ Styles: generate styles for message window frame
+ Styles: generate styles for choice buttons

###other todo:
+ fit screen on mobile
+ renpy.text.extras.ParameterizedText (aka 'show text "qwerty" at truecenter', using <line stop="false"> at custom textbox, hehe)
