# RenPy to WebStoryEngine proof-of-concept converter
# Very simple code for converting most commonly used code structures
# Useful for very simple VNs like "The questions" only!

# =======
# OPTIONS
# =======

init python:
    import os

    # This forces 'dump.dbg' creation, containing parsed data tree
    _LB_DEBUG_FILE_ = True

    # This forces <!-- [DEBUG] ... --> comments in result XML
    _LB_DEBUG_LINES_ = True

    # This forces check of _LB_test_screen decompilation
    _LB_SELFTEST_ = True

    # Renpy label name to start the game with, useful for debug
    _LB_START_LABEL_ = "start"

    # Output directory for resulting WSE project
    _LB_OUTPUT_DIR = config.basedir + os.sep + "www"

    # This forces audio convertion from ogg to mp3 and back
    _LB_CONVERT_AUDIO_ = True

    # Those paths leads to audio converters
    _LB_CONVERT_DIR        =  config.basedir + os.sep + "convert"
    _LB_CONVERT_OGG_TO_WAV = _LB_CONVERT_DIR + os.sep + "oggdec"
    _LB_CONVERT_MP3_TO_WAV = _LB_CONVERT_DIR + os.sep + "mpg123"
    _LB_CONVERT_WAV_TO_MP3 = _LB_CONVERT_DIR + os.sep + "lame"
    _LB_CONVERT_WAV_TO_OGG = _LB_CONVERT_DIR + os.sep + "oggenc2"

# ========
# CONTACTS
# ========
# Copyleft by lolbot, member of IIchan.hk eroge project.
#         _                             
#       ,' ".   ,-"-.                        
#      :     '.'▄██▄ '.
#     :      . ▐█▀ ▐█ ;                     
#     :      ; █▌ ▄█▌,   e r o g a m e       
#      :     ; █▐█▀ /                        
#      '.    ; █   /   _      "  __  __  |          
#       '.   ; █  / |," .''l  | /_/ /   -+-            
#        '.  ; ▌ /  |   l__'  | \__ \__  |              
#         '. ;  /           ._]          [_ 
#          '.; /                          
#           './                          
#            '           
# Written on hard day's nights of pretty nice autumn 2013.
# You can mail me at: lolbot_iichan@mail.ru

# =============
# NO GUARANTIES
# =============
# Please, note, that this code is not perfect.
# IN FACT, THERE ARE ABSULUTELY NO GUARANTIES.
# Some problems must be marked by converter with "<!-- [TODO] -->" comments in generated xml file.
# However, even if there is no such comments, converted code still may be wrong in some way.
# Python is not my native language, so sorry for awful non-pythonic style.

# ======================
# LICENSE? WHAT LICENSE?
# ======================
# It's mostly a Proof Of Concept. You can use this code however you want, I think.
# But be warned, you won't get any presents from Santa, if you delete all the copylefts and introduce this work as your's.

# =========
# CHANGELOG
# =========
# 0.1 - 2013.10.11
#     renpy.ast.Say: simple text by defined characters
#     renpy.ast.UserStatement: play, stop
#     renpy.ast.Translate
#     renpy.ast.EndTranslate
#     renpy.ast.Menu: each block is one jump command
#     renpy.ast.Jump: no expressions
#     renpy.ast.Return
#     renpy.ast.Scene
#     renpy.ast.Show
#     renpy.ast.Hide
#     Runtime: simple menu, jump to rpy_start
# 0.2 - 2013.10.20
#     renpy.ast.With: None, Fade, Dissolve
#     Styles: main menu background
#     Runtime: calling splashscreen, if present
#     Useless: Debug file added
# 0.3 - 2013.10.27
#     convert mp3 to ogg and back             (using console utils)
#     renpy.ast.Python: simple math only      (aka 'x = True', 'x = x + 9', 'x += 1')
#     renpy.ast.If: simple conditions only    (aka 'if x', 'if False', 'else')
#     renpy.ast.Menu: blocks inside branches
#     renpy.ast.Python: renpy.pause calls
#     renpy.ast.UserStatement: pause
#     renpy.ast.With: Pause
# 0.4 - 2014.08.12
#     Styles: config.main_menu_music
#     Styles: config.window_icon
#     Runtime: hide&show textbox during transitions
#     renpy.ast.Say: {{, \n, {i}, {b}, {u}, {s}
#     renpy.ast.Pass
#     renpy.ast.Python: string assignment     (aka 'x = "qwerty"')
#     renpy.ast.If: more simple conditions    (aka 'if x == 0', 'if x == "qwerty"')
#     renpy.ast.Call: no expressions
#     renpy.ast.With: vpunch, hpunch          (aka 'with vpunch')
#     renpy.display.motion.ATLTransform       (aka 'show slavya at right')
# 0.5 - in progress
#     Runtime: toggle textbox on 'h'
#     Runtime: simple help screen
#     Runtime: toggle savegames menu on Right-click
#     Styles: color from who_args
#     Styles: config.windows_icon
#     renpy.ast.With: MoveTransition          (aka 'show slavya at right with move'

# ==============================
# THINGS TO DO IN NEAREST FUTURE
# ==============================
# using <var/>:
#     renpy.ast.Python: more complex math     (aka 'x = y * 3 + 2')
#     renpy.ast.If: refactoring for using nested tags
#     renpy.ast.Menu: refactoring for using nested tags
#     renpy.ast.If: more complex math         (aka 'if x == 2', 'if x > 5 and x < y')
#     renpy.ast.Menu: options with conditions
#     renpy.ast.Jump: expression
#     renpy.ast.Call: expression
# runtime:
#     Runtime: better zorder for bgs and sprites
#     Runtime: toggle fullscreen on 'f'
#     Runtime: toggle fastforward on 'tab'
#     Runtime: fastforward during 'ctrl'
#     Runtime: toggle textbox on Middle-click
# convertion:
#     Convertion: download audio conversion tools
#     Convertion: patch RenPy's script.py file
# styles:
#     Styles: generate hardcoded styles.css
#     Styles: generate styles for default font and text size
#     Styles: generate styles for message window frame
#     Styles: generate styles for choice buttons
# other todo:
#     fit screen on mobile
#     renpy.text.extras.ParameterizedText     (aka 'show text "qwerty" at truecenter', using <line stop="false"> at custom textbox, hehe)

# ==================
# HERE GOES THE CODE
# ==================

init 9999 python:
    import codecs
    import re
    import types
    import subprocess
    import shutil

# ==========================================================
# Here goes parsing process, collecting info from RenPy vars
# ==========================================================

    def trigger_name(k):
        if  k["key"]:
            return "%s_by_%s_%s" % ( k["fn"], k["key"].lower(), k["event"].lower() )
        return "%s_by_%s" % ( k["fn"], k["event"].lower() )        

    def collect_rpy():
        data = {}

        # stage
        data["window_title"] = config.window_title
        data["window_icon"] = config.windows_icon if config.windows_icon else config.window_icon
        data["screen_width"] = config.screen_width
        data["screen_height"] = config.screen_height

        # triggers
        data["keymap"] = [
                {"fn":"savegames", "when":"start",    "label":"Right-click", "event":"contextmenu", "key":None},
                {"fn":"savegames", "when":"start",    "label":"Escape",      "event":"keyup", "key":"ESCAPE"},
                {"fn":"help",      "when":"start",    "label":"F1",          "event":"keyup", "key":"F1"},
                {"fn":"next",      "when":"start",    "label":"Right",       "event":"keyup", "key":"RIGHT_ARROW"},
                {"fn":"next",      "when":"start",    "label":"Enter",       "event":"keyup", "key":"ENTER"},
                {"fn":"next",      "when":"start",    "label":"Space",       "event":"keyup", "key":"SPACE"},
                {"fn":"hidetext",  "when":"newgame",  "label":"h, H",        "event":"keyup", "key":"H"},
                {"fn":"next",      "when":"hidetext", "label":None,          "event":"keyup", "key":"H"},
            ]

        # textbox
        # TODO 
        data["textbox_left"] = 0
        data["textbox_right"] = 0
        data["textbox_top"] = 0
        data["textbox_bottom"] = 0
        data["textbox_yminimum"] = 125

        # characters
        sd = renpy.store.__dict__
        data["characters"] = {}
        for i in sd:
            if  isinstance(sd[i], renpy.character.ADVCharacter):
                data["characters"][i] = {}
                data["characters"][i]["mode"] = sd[i].mode
                data["characters"][i]["displayname"] = sd[i].name
                if  "color" in sd[i].who_args:
                    data["characters"][i]["color"] = sd[i].who_args["color"]

        # images
        imgs = renpy.display.image.images
        data["images_simple"] = dict([(i,img.filename) for i,img in imgs.iteritems() if isinstance(img, renpy.display.im.Image)])
        data["images_simple_packs"] = list(set([i[0] for i in data["images_simple"]]))
        data["images_solid"] = dict([(i,img.color) for i,img in imgs.iteritems() if isinstance(img, renpy.display.imagelike.Solid)])
        data["images_packs"] = list(set(data["images_simple_packs"]+[i[0] for i in data["images_solid"]]))
        data["images_txt"] = dict([(i,img) for i,img in imgs.iteritems() if isinstance(img, renpy.text.extras.ParameterizedText)])
        data["images_scenes"] = set()
        data["images_todo"] = {}
        for i, img in imgs.iteritems():
            if  not i in data["images_simple"].keys() + data["images_solid"].keys() + data["images_txt"].keys():
                data["images_todo"][i] = type(img)
        data["images_with_fade"] = []

        # some styles
        main_menu_background = [i["background"] for i in style.mm_root.properties if "background" in i][-1]
        if  main_menu_background[0] != "#" and "." in main_menu_background:
            data["images_simple"][("bg","main_menu_background")] = main_menu_background
            if  not "bg" in data["images_simple_packs"]:
                data["images_simple_packs"] += ["bg"]
            if  not "bg" in data["images_packs"]:
                data["images_packs"] += ["bg"]

        data["sound"] = {"music":{}}
        if  config.main_menu_music:
            data["sound"]["music"]["main_menu_music"] = config.main_menu_music

        data["branches"] = {}
        for key,value in renpy.game.script.namemap.iteritems():
            if  isinstance(key,unicode) and not key.startswith("_") and not key.endswith("_screen"):
                collect_rpy_branch(key, value.get_children(), data)

        return data

    def branch_name(branch, part):
        return branch if part == 0 else branch + "_part_" + `part+1`

    def collect_rpy_branch(branch,cmds,data,part=0):
        res, parts = parse_rpy_branch(branch,cmds,data,part)
        data["branches"][branch_name(branch, part+parts)] = res
        return parts

    def parse_rpy_branch(branch,cmds,data,part=0):
        result = []
        parts = 0
        for item in cmds:
            if  hasattr(renpy.ast, "Say") and isinstance(item,renpy.ast.Say):
                if  item.who in data["characters"] or item.who is None:
                    result += [ {"type":"say","who":item.who,"what":item.what,"stop":True} ]
                elif re.match('^"[^"]*"$',item.who):
                    who = "undef:"+item.who[1:-1]
                    data["characters"][who] = {"mode":"say","displayname":item.who[1:-1]}
                    result += [ {"type":"say","who":who,"what":item.what,"stop":True} ]
                else:
                    result += [ {"type":"todo","details":"say with unknown character '" + item.who + "': " + item.what} ]

            elif  hasattr(renpy.ast, "UserStatement") and isinstance(item,renpy.ast.UserStatement):
                cmd = re.findall(r'([\w.]+|".*?")', item.line)
                if  cmd[0] == "play" and len(cmd) >= 3:
                    if  cmd[2][0]+cmd[2][-1] == '""' or cmd[2][0]+cmd[2][-1] == "''":
                        fname = cmd[2][1:-1]
                    elif cmd[2] in renpy.store.__dict__:
                        fname = renpy.store.__dict__[cmd[2]]
                    else:
                        fname = None
                    if  fname is not None and isinstance(fname, basestring):
                        channel = cmd[1]
                        parsed = [0, 1, 2]
                        if  'channel' in cmd:
                            channel += "[" + cmd[cmd.index('channel')+1] + "]"
                            parsed += [ cmd.index('channel'), cmd.index('channel')+1 ]
                        if  not channel in data["sound"]:
                            data["sound"][channel] = {}
                        title = ".".join(fname.split(".")[:-1])
                        if  not title in data["sound"][channel]:    
                            data["sound"][channel][title] = fname
                        if  len(cmd) != len(parsed):
                            extras = " ".join([cmd[i] for i in range(len(cmd)) if not i in parsed])
                            result += [{"type":"todo","details":"play statement have extra parameters: "+extras}]
                        result += [{"type":"play","channel":channel,"title":title}]
                    else:
                        result += [ {"type":"todo","details":"UserStatement play : "+item.line} ]
                elif  cmd[0] == "stop" and len(cmd) >= 2:
                    channel = cmd[1]
                    parsed = [0, 1]
                    fadeout = 0.0
                    if  'channel' in cmd:
                        channel += "[" + cmd[cmd.index('channel')+1] + "]"
                        parsed += [ cmd.index('channel'), cmd.index('channel')+1 ]
                    if  'fadeout' in cmd:
                        fadeout = float(cmd[cmd.index('fadeout')+1])
                        parsed += [ cmd.index('fadeout'), cmd.index('fadeout')+1 ]
                    if  fadeout == 0.0:
                        result += [{"type":"stop","channel":channel,"fade":False}]
                    else:
                        result += [{"type":"stop","channel":channel,"fade":True,"fadeout":fadeout}]
                    if  len(cmd) != len(parsed):
                        extras = " ".join([cmd[i] for i in range(len(cmd)) if not i in parsed])
                        result += [{"type":"todo","details":"stop statement have extra parameters: "+extras}]
                elif  cmd[0] == "pause":
                    if  len(cmd) == 1:
                        result += [{"type":"pause","time":None}]
                    else:
                        result += [{"type":"pause","time":float(cmd[1])}]
                        if  len(cmd) > 2:
                            result += [{"type":"todo","details":"pause statement have extra parameters: "+" ".join(cmd[2:])}]
                else:
                    result += [ {"type":"todo","details":"UserStatement : "+item.line} ]

            elif  hasattr(renpy.ast, "Translate") and isinstance(item,renpy.ast.Translate):
                r, p = parse_rpy_branch(branch,item.block,data)
                result += r
            elif  hasattr(renpy.ast, "EndTranslate") and isinstance(item,renpy.ast.EndTranslate):
                pass
            elif  hasattr(renpy.ast, "Pass") and isinstance(item,renpy.ast.Pass):
                result += [ {"type":"debug","details":"pass"} ]

            elif  hasattr(renpy.ast, "Python") and isinstance(item,renpy.ast.Python):
                match = re.match('^ *([_a-zA-Z0-9]*) *= *(?:\'([^\']*)\'|"([^"]*)") *$',item.code.source)
                if  match:
                    result += [ {"type":"debug","details":"python rule #1: "+item.code.source} ]
                    val = match.group(3) if match.group(2) is None else match.group(2)
                    result += [ {"type":"python","action":"set","name":match.group(1),"value":val} ]
                    continue
                match = re.match('^ *([_a-zA-Z0-9]*) *= *(True|False|[0-9]+|-[0-9]+) *$',item.code.source)
                if  match:
                    result += [ {"type":"debug","details":"python rule #2: "+item.code.source} ]
                    val = "1" if match.group(2) == "True" else "0" if match.group(2) == "False" else match.group(2)
                    result += [ {"type":"python","action":"set","name":match.group(1),"value":val} ]
                    continue
                match = re.match('^ *([_a-zA-Z0-9]*) *= *([_a-zA-Z0-9]*) *([+-]) *([1-9]) *$',item.code.source)
                if  match and match.group(1) == match.group(2):
                    result += [ {"type":"debug","details":"python rule #3: "+item.code.source} ]
                    act = "increase" if match.group(3) == "+" else "decrease"
                    result += [ {"type":"python","action":act,"name":match.group(1)} ] * int(match.group(4))
                    continue
                match = re.match('^ *([_a-zA-Z0-9]*) *([+-])= *([1-9]) *$',item.code.source)
                if  match:
                    result += [ {"type":"debug","details":"python rule #4: "+item.code.source} ]
                    act = "increase" if match.group(2) == "+" else "decrease"
                    result += [ {"type":"python","action":act,"name":match.group(1)} ] * int(match.group(3))
                    continue
                match = re.match('^ *renpy.([_a-zA-Z0-9.]*)\((.*)\) *$',item.code.source)
                if  match:
                    result += [ {"type":"debug","details":"python rule #5: "+item.code.source} ]
                    func = match.group(1)
                    args = match.group(2)
                    if  func == "pause" and not "," in args:
                        result += [{"type":"pause","time":None if  re.match('^ *$',args) else float(args)}]
                    else:
                        result += [ {"type":"todo","details":"build-in function %s with args: %s" % (func,args) } ]
                    continue
                result += [ {"type":"todo","details":"python: "+item.code.source} ]

            elif  hasattr(renpy.ast, "Menu") and isinstance(item,renpy.ast.Menu) or  hasattr(renpy.ast, "If") and isinstance(item,renpy.ast.If):
                links = []
                parts_new = parts + 1
                has_question = False
                if  hasattr(renpy.ast, "Menu") and isinstance(item,renpy.ast.Menu):
                    items = []
                    for (optionId,(txt, condition, block)) in enumerate(item.items):
                        if  block is None:
                            result += [ {"type":"say","who":"narrator","what":txt,"stop":False} ]
                            has_question = True
                        elif  len(block) == 1 and hasattr(renpy.ast, "Jump") and isinstance(block[0],renpy.ast.Jump) and not block[0].expression:
                            items += [ (txt, block[0].target, condition) ]
                        else:
                            bname = branch_name(branch,part+parts_new)
                            parts_new += collect_rpy_branch(branch,block,data,part+parts_new) + 1
                            links += [part+parts_new - 1]
                            items += [ (txt, bname, condition) ]
                    result += [ {"type":"menu","items":items,"has_question":has_question} ]
                else:
                    for (optionId,(condition, block)) in enumerate(item.entries):
                        if  len(block) == 1 and hasattr(renpy.ast, "Jump") and isinstance(block[0],renpy.ast.Jump) and not block[0].expression:
                            bname = block[0].target
                        else:
                            bname = branch_name(branch,part+parts_new)
                            parts_new += collect_rpy_branch(branch,block,data,part+parts_new) + 1
                            links += [part+parts_new-1]

                        match = re.match('^ *([_a-zA-Z0-9]*) *$',condition)
                        if  match:
                            result += [ {"type":"debug","details":"if condition rule #1: "+condition} ]
                            if  match.group(1) == "True":
                                result += [ {"type":"jump","target":bname} ]
                            elif  match.group(1) == "False":
                                pass
                            else:
                                result += [ {"type":"jump_if","target":bname,"condition":match.group(1)} ]
                            continue
                        match = re.match('^ *([_a-zA-Z0-9]*) *== *(?:\'([^\']*)\'|"([^"]*)") *$',condition)
                        if  match:
                            result += [ {"type":"debug","details":"if condition rule #2: "+condition} ]
                            val = match.group(3) if match.group(2) is None else match.group(2)
                            result += [ {"type":"jump_if_eq","target":bname,"name":match.group(1),"value":val} ]
                            continue
                        match = re.match('^ *([_a-zA-Z0-9]*) *== *(True|False|[0-9]+|-[0-9]+) *$',condition)
                        if  match:
                            result += [ {"type":"debug","details":"if condition rule #3: "+condition} ]
                            val = "1" if match.group(2) == "True" else "0" if match.group(2) == "False" else match.group(2)
                            result += [ {"type":"jump_if_eq","target":bname,"name":match.group(1),"value":val} ]
                            continue
                        result += [ {"type":"todo","details":"jump to "+bname+" if "+condition} ]
                jname = branch_name(branch,part+parts_new)
                for l in links:
                    data["branches"][branch_name(branch,l)] += [ {"type":"jump","target":jname} ]
                result += [ {"type":"jump","target":jname} ]
                data["branches"][branch_name(branch,part+parts)] = result
                parts = parts_new
                result = []

            elif  hasattr(renpy.ast, "Call") and isinstance(item,renpy.ast.Call):
                if  not item.expression and not item.arguments:
                    result += [ {"type":"call","target":item.label} ]
                else:
                    result += [ {"type":"todo","details":"call with expression or arguments: "+item.label} ]

            elif  hasattr(renpy.ast, "Jump") and isinstance(item,renpy.ast.Jump):
                if  not item.expression:
                    result += [ {"type":"jump","target":item.target} ]
                else:
                    result += [ {"type":"todo","details":"jump expression: "+item.target} ]
                break
            elif  hasattr(renpy.ast, "Return") and isinstance(item,renpy.ast.Return):
                break

            elif  (hasattr(renpy.ast, "Scene") and isinstance(item,renpy.ast.Scene)) or (hasattr(renpy.ast, "Show") and isinstance(item,renpy.ast.Show)) or (hasattr(renpy.ast, "Hide") and isinstance(item,renpy.ast.Hide)):
                zorder = 0
                expression = None
                tag = None
                behind = []
                if len(item.imspec) == 3:
                    iname, at_list, layer = item.imspec
                elif len(item.imspec) == 6:
                    iname, expression, tag, at_list, layer, zorder = item.imspec
                elif len(item.imspec) == 7:
                    iname, expression, tag, at_list, layer, zorder, behind = item.imspec
                if  not expression:
                    t = "scene" if isinstance(item,renpy.ast.Scene) else "show" if isinstance(item,renpy.ast.Show) else "hide"
                    if  t == "scene":
                        data["images_scenes"].add(iname[0])
                    at = None

                    if  zorder:
                        result += [ {"type":"todo","details":t+" option zorder: " + `zorder`} ]
                    if  tag:
                        result += [ {"type":"todo","details":t+" option tag: "+`tag`} ]
                    if  behind:
                        result += [ {"type":"todo","details":t+" option behind: "+`behind`} ]
                    if  layer != "master":
                        result += [ {"type":"todo","details":t+" option layer: "+`layer`} ]

                    if  at_list:
                        if len(at_list) == 1 and at_list[0].rstrip() in ["center","left","right"]:
                            at = at_list[0].rstrip()
                        else:
                            result += [ {"type":"todo","details":t+" option at_list: "+`at_list`} ]

                    if  t == "show" and iname[:-1] in data["images_txt"]:
                        result += [ {"type":"say","who":" ".join(iname[:-1]),"what":iname[-1][1:-1],"stop":False} ]
                    elif  t == "hide" and iname in data["images_txt"]:
                        result += [ {"type":"todo","details":"hide renpy.text.extras.ParameterizedText: " + " ".join(iname)} ]
                    else:                        
                        result += [ {"type":t,"asset":iname[0],"image":" ".join(iname[1:]),"at":at} ]
                else:
                    result += [ {"type":"todo","details":"show expression: "+expression} ]

            elif  hasattr(renpy.ast, "With") and isinstance(item,renpy.ast.With):
                func, args, kwargs = "None", tuple(), {}
                if  item.expr in ["hpunch", "vpunch"]:
                    func = item.expr
                    args = []
                    kwargs = {}
                else:
                    wth = eval(unicode(item.expr),globals())
                    if  wth is not None:
                        func, args = wth.callable.__name__, wth.args
                        kwargs = dict([(i,j) for (i,j) in wth.kwargs.iteritems()])
                r = {"type":"with_begin","func":func,"args":args,"kwargs":kwargs}
                for id in range(len(result)-1,-1,-1):
                    if  result[id]["type"] not in ["show","hide","scene"]:
                        result.insert(id+1,r)
                        break
                else:
                    result = [r] + result
                result += [ {"type":"with_end","func":func,"args":args,"kwargs":kwargs} ]
                if  func == "Fade":
                    clr = color(kwargs["color"]) if "color" in kwargs else (0,0,0,255)
                    if  not clr in data["images_with_fade"]:
                        data["images_with_fade"] += [clr]

            else:
                result += [ {"type":"todo","details":"unknown command: "+`type(item)`} ]
        return result, parts

# ====================================
# Here goes music convertation callers
# ====================================

    def convert_music(source,ext):
        title = ".".join(source.split(".")[:-1])
        source_ext = source.split(".")[-1]

        if  source_ext == ext:
            return True, "Nothing to convert"

        if  not _LB_CONVERT_AUDIO_:
            return False, "convertation is disabled, '_LB_CONVERT_AUDIO_' is not 'True'"

        srcfile = _LB_OUTPUT_DIR + os.sep + "game" + os.sep + source.replace("/",os.sep)
        wavfile = config.basedir + os.sep + "temp.wav"
        dstfile = _LB_OUTPUT_DIR + os.sep + "game" + os.sep + title.replace("/",os.sep) + "." + ext

        if  os.path.exists(wavfile):
            os.unlink(wavfile)

        if  not os.path.exists(srcfile):
            return False, "Source missing!"

        if  os.path.exists(dstfile):
            return True, "Already converted?"

        if  source_ext == "wav":
            wavfile = srcfile
        elif  source_ext == "mp3":
            cmd = '"%s" -w "%s" "%s"' % (_LB_CONVERT_MP3_TO_WAV, wavfile, srcfile)
            sub = subprocess.Popen(cmd, stderr=subprocess.STDOUT,stdout = subprocess.PIPE )
            out, err = sub.communicate()
            if  sub.wait() != 0:
                return False, "running '%s' failed" % _LB_CONVERT_MP3_TO_WAV
        elif  source_ext == "ogg":
            cmd = '"%s" -w "%s" "%s"' % (_LB_CONVERT_OGG_TO_WAV, wavfile, srcfile)
            sub = subprocess.Popen(cmd, stderr=subprocess.STDOUT,stdout = subprocess.PIPE )
            out, err = sub.communicate()
            if  sub.wait() != 0:
                return False, "running '%s' failed" % _LB_CONVERT_OGG_TO_WAV
        else:
            return False, "unknown source extention: " + source_ext

        if  ext == "wav":
            shutil.copy2(wavfile,dstfile)
        elif  ext == "mp3":
            cmd = '"%s" "%s" "%s"' % (_LB_CONVERT_WAV_TO_MP3, wavfile, dstfile)
            if  subprocess.call(cmd) != 0:
                return False, "running '%s' failed" % _LB_CONVERT_WAV_TO_MP3
        elif  ext == "ogg":
            cmd = '"%s" -o "%s" "%s"' % (_LB_CONVERT_WAV_TO_OGG, dstfile, wavfile)
            if  subprocess.call(cmd) != 0:
                return False, "running '%s' failed" % _LB_CONVERT_WAV_TO_OGG
        else:
            return False, "unknown destination extention: " + ext

        if  source_ext != "wav":
            os.unlink(wavfile)

        return True, "Converted successfully"

# ==================================================
# Here goes final result generation from parsed data
# ==================================================

    def generate_html(data):
        result = ""
        result +=  """<!DOCTYPE html>\n<html>\n    <head>\n        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n"""
        result += """        <title>%s</title>\n""" % data["window_title"]
        result += """        <link rel="stylesheet" href="styles.css" type="text/css" />\n"""
        if  data["window_icon"]:
            result += """        <link rel="icon" href="favicon.png" type="image/png" />\n"""
        result += """    </head>\n"""
        result += """    <body>\n        <script src="js/WebStoryEngine.js"></script>\n        <script>\n"""
        result += """            var game = new WSE.Game({ url: "game.xml", host: typeof HOST === "undefined" ? false : HOST });\n"""
        result += """            game.start();\n        </script>\n    </body>\n</html>"""
        return result
    
    def generate_xml_settings(data):
        result = ""

        #<settings><stage>
        width, height = data["screen_width"], data["screen_height"]
        result += """        <stage width="%dpx" height="%dpx" id="Stage" create="yes" center="yes" />\n""" % (width, height)

        #<settings><triggers>
        result += """        <triggers>\n"""
        for k in data["keymap"]:
            result += """            <trigger event="%s" """ % k["event"]
            if  k["key"]:
                result += """key="%s" """ % k["key"]
            if  k["fn"] in [ "next" ]:
                result += """special="%s" """ % k["fn"]
            elif k["fn"] in [ "savegames", "stageclick_enable", "stageclick_disable" ]:                
                result += """function="%s" """ % k["fn"]
            else:
                result += """scene="%s" """ % k["fn"]
            result += """name="%s" />\n""" % trigger_name(k)
        result += """        </triggers>\n"""

        return result

    def generate_xml_assets(data):
        result = ""

        #<assets><textbox>
        width, height = data["screen_width"], data["screen_height"]
        left, right = data["textbox_left"], data["textbox_right"]
        top, bottom = data["textbox_top"], data["textbox_bottom"]
        sizes = (left, height-data["textbox_yminimum"]-bottom, width-left-right, data["textbox_yminimum"])
        result += """        <textbox name="tb_adv" behaviour="adv" cssid="tb_adv" x="%dpx" y="%dpx" width="%dpx" height="%dpx">\n""" % sizes
        result += """            <nameTemplate>{name}<br /></nameTemplate>\n        </textbox>\n""" 
        sizes = (left, top, width-left-right, height-top-bottom)
        result += """        <textbox name="tb_nvl" behaviour="nvl" cssid="tb_nvl" x="%dpx" y="%dpx" width="%dpx" height="%dpx">\n""" % sizes
        result += """            <nameTemplate>{name}<br /></nameTemplate>\n        </textbox>\n""" 

        #<assets><character>
        for name, c in data["characters"].iteritems():
            result += """        <character name="%s" textbox="%s">""" % (name, "tb_adv" if c["mode"] == "say" else "tb_nvl")
            if  c["displayname"] != None:
                if  "color" in c:
                    result += """<displayname><font color="%s">%s</font></displayname>""" % (c["color"], c["displayname"])
                else:
                    result += """<displayname>%s</displayname>""" % c["displayname"]
            result += """</character>\n"""
        for c in data["images_txt"]:
            result += """        <!-- [TODO] Not a simple character: %s -->\n""" % (" ".join(c))

        #<assets><imagepack>
        #<assets><curtain>
        for i in sorted(data["images_simple_packs"],key=lambda x: x not in data["images_scenes"]):
            result += """        <imagepack name="%s">\n""" % i
            for name, img in data["images_simple"].iteritems():
                if  name[0] == i:
                    result += """            <image name="%s" src="%s" />\n""" % (" ".join(name[1:]), "game/"+img)
            result += """        </imagepack>\n"""
        for i, clr in data["images_solid"].iteritems():
            result += """        <curtain name="%s" color="rgba(%d,%d,%d,%.2f)" z="0" />\n""" % (" ".join(i), clr[0], clr[1], clr[2], clr[3]/255.0)
        for clr in data["images_with_fade"]:
            result += """        <curtain name="with Fade: %s" color="rgba(%d,%d,%d,%.2f)" />\n""" % (`clr`, clr[0], clr[1], clr[2], clr[3]/255.0)
        for i, t in data["images_todo"].iteritems():
            result += """        <!-- [TODO] Not a simple image: %s = %s -->\n""" % (" ".join(i), `t`)

        #<assets><audio>
        for channel, sounds in data["sound"].iteritems():
            #TODO check channel object, not it's name
            loop = "true" if channel.startswith("music") else "false"
            result += """        <audio name="%s" loop="%s" fade="false">\n""" % (channel, loop)
            for id, sound in sounds.iteritems():
                title = ".".join(sound.split(".")[:-1])
                result += """            <track title="%s">\n""" % id
                for e in ["mp3","ogg"]:
                    res, reason = convert_music(sound,e)
                    if  res:
                        result += """                <source href="game/%s.%s" type="%s" />\n""" % (title,e,e)
                    else:
                        result += """                <!-- [TODO] convert "game/%s" to "game/%s.%s failed: %s" -->\n""" % (sound,title,e,reason)
                result += """            </track>\n"""
            result += """        </audio>\n"""

        return result
        
    def generate_xml_scenes_builtin(data):
        result = ""

        #<scenes><scene id="start">
        result += """        <scene id="start">\n"""
        for k in data["keymap"]:
            if  k["when"] == "start":
                result += """            <trigger name="%s" action="activate" />\n""" % trigger_name(k)
        for im in data["images_packs"]:
            result += """            <var action="set" name="is_%s_visible" value="false" />\n""" % (im)
        if  "splashscreen" in data["branches"]:
            result += """            <sub scene="rpy_splashscreen" />\n"""
            for im in data["images_packs"]:
                result += """            <hide asset="%s" ifvar="is_%s_visible" ifvalue="true" duration="0" />\n""" % (im,im)
                result += """            <var action="set" name="is_%s_visible" value="false" />\n""" % (im)
        if  "main_menu_music" in data["sound"]["music"]:
            result += """            <set asset="music" track="main_menu_music" />\n"""
            result += """            <play asset="music" />\n"""
        result += """            <goto scene="menu" />\n        </scene>\n"""

        #<scenes><scene id="menu">
        result += """        <scene id="menu">\n"""
        if  ("bg","main_menu_background") in data["images_simple"]:
            result += """            <set asset="bg" image="main_menu_background" duration="0" />\n"""
            result += """            <show asset="bg" ifvar="is_bg_visible" ifvalue="false" duration="0" />\n"""
            result += """            <var action="set" name="is_bg_visible" value="true" />\n"""
        result += """            <choice>\n"""
        result += """                <option label="Start Game" scene="newgame" />\n"""
        result += """                <option label="Load Game" scene="saveload" />\n"""
        result += """                <option label="Help"><sub scene="help" /></option>\n"""
        result += """            </choice>\n            <goto scene="menu" />\n        </scene>\n"""

        #<scenes><scene id="newgame">
        result += """        <scene id="newgame">\n"""
        for k in data["keymap"]:
            if  k["when"] == "newgame":
                result += """            <trigger name="%s" action="activate" />\n""" % trigger_name(k)
        result += """            <sub scene="rpy_%s" />\n""" % _LB_START_LABEL_
        for k in data["keymap"]:
            result += """            <trigger name="%s" action="deactivate" />\n""" % trigger_name(k)
        result += """            <hide asset="tb_nvl" duration="0" />\n"""
        result += """            <hide asset="tb_adv" duration="0" />\n"""
        result += """            <wait />\n            <restart/>\n        </scene>\n"""

        #<scenes><scene id="saveload">
        result += """        <scene id="saveload">\n            <fn name="savegames" />\n            <goto scene="menu" />\n        </scene>\n"""

        #<scenes><scene id="help">
        result += '        <scene id="help">\n            <alert title="Key and Mouse Bindings:" message="'
        keys = ["Left-click"] + [k["label"] for k in data["keymap"] if k["label"] and k["fn"]=="next"]
        result += """{u}%s:{/u}{br/}    Advances through the game.{br/}""" % ", ".join(keys)
        keys = [k["label"] for k in data["keymap"] if k["label"] and k["fn"]=="savegames"]
        result += """{u}%s:{/u}{br/}    Enters the save / load menu.{br/}""" % ", ".join(keys)
        keys = [k["label"] for k in data["keymap"] if k["label"] and k["fn"]=="hidetext"]
        result += """{u}%s:{/u}{br/}    Toggles text window visibility.{br/}""" % ", ".join(keys)
        keys = [k["label"] for k in data["keymap"] if k["label"] and k["fn"]=="help"]
        result += """{u}%s:{/u}{br/}    Shows this help screen.{br/}""" % ", ".join(keys)
        result += '"/>\n        </scene>\n'

        #<scenes><scene id="hidetext">
        result += """        <scene id="hidetext">\n"""
        for k in data["keymap"]:
            if  k["fn"] == "hidetext":
                result += """            <trigger name="%s" action="deactivate" />\n""" % trigger_name(k)
        for s in ["tb_adv", "tb_nvl"]:
                result += """            <hide asset="%s" duration="0" ifvar="is_%s_visible" ifvalue="true"/>\n""" % ( s, s )
        for k in data["keymap"]:
            if  k["when"] == "hidetext":
                result += """            <trigger name="%s" action="activate" />\n""" % trigger_name(k)
        result += """            <break />\n"""
        for k in data["keymap"]:
            if  k["when"] == "hidetext":
                result += """            <trigger name="%s" action="deactivate" />\n""" % trigger_name(k)
        for s in ["tb_adv", "tb_nvl"]:
                result += """            <show asset="%s" duration="0" ifvar="is_%s_visible" ifvalue="true"/>\n""" % ( s, s )
        for k in data["keymap"]:
            if  k["fn"] == "hidetext":
                result += """            <trigger name="%s" action="activate" />\n""" % trigger_name(k)
        result += """            <break />\n        </scene>\n"""


        return result

    def update_textbox(is_visible, mode=None):
        result = ""
        other_modes = ["nvl"] if mode == "say" else ["say"] if mode == "nvl" else ["say","nvl"]
        if  mode is not None:
            if  is_visible[mode] is not True:
                result += """            <show asset="%s" duration="0" />\n""" % ("tb_adv" if mode=="say" else "tb_nvl")
                result += """            <var action="set" name="is_%s_visible" value="true" />\n""" % ("tb_adv" if mode=="say" else "tb_nvl")
                is_visible[mode] = True
        for mode in other_modes:
            if  is_visible[mode] is not False:
                result += """            <clear asset="%s" />\n""" % ("tb_adv" if mode=="say" else "tb_nvl")
                result += """            <hide asset="%s" duration="0" />\n""" % ("tb_adv" if mode=="say" else "tb_nvl")
                result += """            <var action="set" name="is_%s_visible" value="false" />\n""" % ("tb_adv" if mode=="say" else "tb_nvl")
                is_visible[mode] = False
        return result

    def generate_xml_scenes(data):
        result = ""
        for key in sorted(data["branches"].keys()):
            dissolve_duration = 0
            move_duration = 0
            is_visible = {"nvl":None, "say":None}
            result += """        <scene id="rpy_%s">\n""" % key
            for item in data["branches"][key]:
        #say
                if  item["type"] == "say":
                    for (r,c) in [
                            ('{{','_LB_MAGICAL_CURLY_BRACE_'), 
                            ('&','&amp;'), ('"','&quot;'), ("'",'&apos;'), ('<','&lt;'), ('>','&gt;'),
                            ('{i}','<i>'), ('{/i}','</i>'), ('{b}','<b>'), ('{/b}','</b>'),
                            ('{s}','<s>'), ('{/s}','</s>'), ('{u}','<u>'), ('{/u}','</u>'),
                            ('_LB_MAGICAL_CURLY_BRACE_','{'), ('\n','<br/>')
                        ]:
                        item["what"] = item["what"].replace(r,c)
                    #TODO style:   {a=label}, {a=http://...}, {color=f00}, {font=filename.ttf}, {image=filename}, {plain}, {size=spec}, {=style}
                    #TODO control: {fast}, {nw}, {p}, {w}, {w=.5}
                    for (r,c) in [ ]:
                        item["what"] = item["what"].replace(r,c)
                    who = item["who"] if item["who"] is not None else "narrator"
                    if  who in data["characters"]:
                        mode = data["characters"][who]["mode"]
                        result += update_textbox(is_visible, mode)
                        if  item["stop"]:
                            result += """            <line s="%s">%s</line>\n""" % (who, item["what"])
                        else:
                            result += """            <line s="%s" stop="false">%s</line>\n""" % (who, item["what"])
                    else:
                        result += """            <!-- [TODO] line s="%s" stop="false" text="%s" -->\n""" % (who, item["what"])

        #sound
                elif item["type"] == "play":
                    result += """            <set asset="%s" track="%s" />\n""" % (item["channel"],item["title"])
                    result += """            <play asset="%s" />\n""" % (item["channel"])
                elif item["type"] == "stop":
                    if  item["fade"]:
                        result += """            <stop asset="%s" fade="true" fadeout="%d"/>\n""" % (item["channel"],item["fadeout"]*1000)
                    else:
                        result += """            <stop asset="%s" />\n""" % (item["channel"])

        #python
                elif item["type"] == "python":
                    if  item["action"] == "set":
                        result += """            <var name="%s" action="set" value="%s" />\n""" % (item["name"],item["value"])
                    else:
                        result += """            <var name="%s" action="%s" />\n""" % (item["name"],item["action"])

        #pause
                elif item["type"] == "pause":
                    result += update_textbox(is_visible)
                    if  item["time"] is None:
                        result += """            <break />\n"""
                    else:
                        result += """            <wait duration="%d" />\n""" % ( item["time"]*1000 )
                        result += """            <wait />\n"""

        #jumps
                #FIXME: remove 'jump_if_eq' when python math converter is ready
                elif item["type"] == "jump_if_eq": 
                    result += """            <goto scene="rpy_%s" ifvar="%s" ifvalue="%s"/>\n""" % (item["target"],item["name"],item["value"])
                elif item["type"] == "jump_if":
                    result += """            <goto scene="rpy_%s" ifvar="%s" ifnot="0"/>\n""" % (item["target"],item["condition"])
                elif item["type"] == "jump":
                    result += """            <goto scene="rpy_%s" />\n""" % (item["target"])
                elif item["type"] == "call":
                    result += """            <sub scene="rpy_%s" />\n""" % (item["target"])
                    is_visible = {"nvl":None, "say":None}

        #menu
                elif item["type"] == "menu":
                    if  not item["has_question"]:
                        result += update_textbox(is_visible)
                    result += """            <choice>\n"""
                    for (label, target, condition) in item["items"]:
                        if  condition == "True":
                            result += """                <option label="%s" scene="rpy_%s" />\n""" % (label, target)
                        else:
                            result += """                <!-- [TODO] option label="%s" scene="rpy_%s" condition="%s" -->\n""" % (label, target, condition)
                    result += """            </choice>\n"""

        #scene, show, hide
                elif item["type"] == "scene":
                    for im in data["images_packs"]:
                        if  im !=  item["asset"]:
                            result += """            <hide asset="%s" ifvar="is_%s_visible" ifvalue="true" duration="%d" />\n""" % (im,im,dissolve_duration)
                            result += """            <var action="set" name="is_%s_visible" value="false" />\n""" % (im)
                    if  dissolve_duration > 0:
                        result += update_textbox(is_visible)
                        result += """            <set asset="%s" ifvar="is_%s_visible" ifvalue="true" image="%s" duration="%d" />\n""" % (item["asset"],item["asset"],item["image"],dissolve_duration)
                        result += """            <set asset="%s" ifvar="is_%s_visible" ifvalue="false" image="%s" duration="0" />\n""" % (item["asset"],item["asset"],item["image"])
                    else:
                        result += """            <set asset="%s" image="%s" duration="0" />\n""" % (item["asset"],item["image"])
                    result += """            <move asset="%s" x="50%%" xAnchor="50%%" y="100%%" yAnchor="100%%" duration="%d" />\n""" % (item["asset"],move_duration)
                    result += """            <show asset="%s" ifvar="is_%s_visible" ifvalue="false" duration="%d" />\n""" % (item["asset"],item["asset"],dissolve_duration)
                    result += """            <var action="set" name="is_%s_visible" value="true" />\n""" % (item["asset"])
                elif item["type"] == "show":
                    if  dissolve_duration > 0:
                        result += update_textbox(is_visible)
                        result += """            <set asset="%s" ifvar="is_%s_visible" ifvalue="true" image="%s" duration="%d" />\n""" % (item["asset"],item["asset"],item["image"],dissolve_duration)
                        result += """            <set asset="%s" ifvar="is_%s_visible" ifvalue="false" image="%s" duration="0" />\n""" % (item["asset"],item["asset"],item["image"])
                    else:
                        result += """            <set asset="%s" image="%s" duration="0" />\n""" % (item["asset"],item["image"])
                    if  item["at"] in ["center",None]:
                        result += """            <move asset="%s" x="50%%" xAnchor="50%%" y="100%%" yAnchor="100%%" duration="%d" />\n""" % (item["asset"],move_duration)
                    elif item["at"] == "left":
                        result += """            <move asset="%s" x="0%%" xAnchor="0%%" y="100%%" yAnchor="100%%" duration="%d" />\n""" % (item["asset"],move_duration)
                    elif item["at"] == "right":
                        result += """            <move asset="%s" x="100%%" xAnchor="100%%" y="100%%" yAnchor="100%%" duration="%d" />\n""" % (item["asset"],move_duration)
                    result += """            <show asset="%s" ifvar="is_%s_visible" ifvalue="false" duration="%d" />\n""" % (item["asset"],item["asset"],dissolve_duration)
                    result += """            <var action="set" name="is_%s_visible" value="true" />\n""" % (item["asset"])
                elif item["type"] == "hide":
                    if  dissolve_duration > 0:
                        result += update_textbox(is_visible)
                    result += """            <hide asset="%s" ifvar="is_%s_visible" ifvalue="true" duration="%d" />\n""" % (item["asset"],item["asset"],dissolve_duration)
                    result += """            <var action="set" name="is_%s_visible" value="false" />\n""" % (item["asset"])

        #with
                elif item["type"] == "with_begin":
                    if  item["func"] in ["None", "NoTransition"]:
                        pass
                    elif item["func"] == "MoveTransition":
                        result += update_textbox(is_visible)
                        move_duration = int( item["args"][0]*1000 )
                    elif item["func"] == "Dissolve":
                        result += update_textbox(is_visible)
                        dissolve_duration = int( item["args"][0]*1000 )
                    elif item["func"] == "Fade":
                        result += update_textbox(is_visible)
                        clr = color(item["kwargs"]["color"]) if "color" in item["kwargs"] else (0,0,0,255)
                        result += """            <show asset="with Fade: %s" duration="%d" />\n""" % ( `clr`,item["args"][0]*1000 )
                        result += """            <wait />\n"""
                        if  item["args"][2] != 0.0:
                            result += """            <wait duration="%d" />\n""" % ( item["args"][1]*1000 )
                    elif item["func"] in ["hpunch", "vpunch"]:
                        pass
                    else:
                        result += """            <!-- [TODO] here begins with %s%s%s -->\n""" % (item["func"], `item["args"]`, `item["kwargs"]`)
                elif item["type"] == "with_end":
                    if  item["func"] == "None":
                        pass
                    elif item["func"] == "MoveTransition":
                        if  move_duration > 0:
                            result += """            <wait />\n"""
                        move_duration = 0
                    elif item["func"] == "Dissolve":
                        if  dissolve_duration > 0:
                            result += """            <wait />\n"""
                        dissolve_duration = 0
                    elif item["func"] == "Fade":
                        clr = color(item["kwargs"]["color"]) if "color" in item["kwargs"] else (0,0,0,255)
                        result += """            <hide asset="with Fade: %s" duration="%d" />\n""" % ( `clr`,item["args"][2]*1000 )
                        result += """            <wait />\n"""
                    elif item["func"] == "NoTransition":
                        result += """            <wait duration="%d" />\n""" % ( item["args"][0]*1000 )
                        result += """            <wait />\n"""
                    elif item["func"] == "hpunch":
                        for im in data["images_packs"]:
                            result += """            <shake asset="%s" ifvar="is_%s_visible" ifvalue="true" dx="-15px" />\n""" % (im,im)
                        result += """            <wait />\n"""
                    elif item["func"] == "vpunch":
                        for im in data["images_packs"]:
                            result += """            <shake asset="%s" ifvar="is_%s_visible" ifvalue="true" dx="-10px" />\n""" % (im,im)
                        result += """            <wait />\n"""
                    else:    
                        result += """            <!-- [TODO] here ends with %s%s%s -->\n""" % (item["func"], `item["args"]`, `item["kwargs"]`)                    

        #other
                elif item["type"] == "todo":
                    result += """            <!-- [TODO] %s -->\n""" % item["details"]
                elif item["type"] == "debug":
                    if  _LB_DEBUG_LINES_:
                        result += """            <!-- [DEBUG] %s -->\n""" % item["details"]
                else:
                    renpy.error(item)
            result += """        </scene>\n"""

        return result

    def generate_xml(data):
        result =  """<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n<ws>\n"""
        result += """     <settings>\n"""
        result += generate_xml_settings(data)
        result += """    </settings>\n"""
        result += """    <assets>\n"""
        result += generate_xml_assets(data)
        result += """    </assets>\n"""
        result += """    <scenes>\n"""
        result += generate_xml_scenes_builtin(data)
        result += generate_xml_scenes(data)
        result += """    </scenes>\n"""
        result += """</ws>"""
        return result

# ============
# Debug dumper
# ============

#
#                        ▄▄▄███████▄▄▄
#                    ▄▄██▀▀▀       ▀▀▀██▄▄  
#                 ▄██▀▀                 ▀▀██▄   
#               ▄█▀                         ▀█▄    
#             ▄█▀        \   '. .'   /      ██▀█▄  
#           ▄█▀           \ __▄█▄__ /     ███   ▀█▄ 
#          ▐█▌    ~.    _▄▄█▀█████▀█▄▄.  ██,~    ▐█▌
#          ██       '. .▄▄▄▄███████▄▄▄▄███'       ██
#         ▐█▌         ;░░░░░░▐███▌░░░░██;         ▐█▌
#         ██         ;░■░░░░░░▀█▀░░░███░░;         ██
#        ▐█▌         .░░░░░■░░░|░░░██░░░░.         ▐█▌
#        ▐█▌      ~~~;░░░░░░░░░|░███░░░░░;~~~      ▐█▌
#        ▐█          ;░░░■░░░░░|██░░░■░░░;          █▌
#        ▐█▌         ;░░░░░░░░███░░░░░░░░;         ▐█▌
#        ▐█▌         ;░░░░░░░██|░░░░░░░░░;         ▐█▌
#         ██         .░■░░░███░|░■░░░░░■░.         ██
#         ▐█▌      .' ;░░░██░░░|░░░░░░░░; '.      ▐█▌
#          ██    ~'    '███░■░░|░░■░░░░'    '~    ██
#          ▐█▌         ██.░░░░░|░░░░░.'          ▐█▌
#           ▀█▄      ███    ''-lb''             ▄█▀
#             ▀█▄   ██                        ▄█▀
#               ▀████                       ▄█▀
#                 ▀██▄▄                 ▄▄██▀
#                    ▀▀██▄▄▄       ▄▄▄██▀▀  
#                        ▀▀▀███████▀▀▀
#

    def generate_dbg(data, tab=0):
        result = ""
        if  isinstance(data, dict):
            keys = sorted(data.keys())
        else:
            keys = range(len(data))
        if  "type" in keys:
            result += "    "*tab + "<%s>\n" % (data["type"])
        for k in keys:
            if  k == "type":
                pass
            elif isinstance(data[k], (str, unicode)):
                result += "    "*tab + "%s: %s\n" % (k,data[k])
            elif isinstance(data[k], (int, float, type(None))):
                result += "    "*tab + "%s: %s\n" % (k,`data[k]`)
            elif isinstance(data[k], (dict, list, tuple, types.DictType)):
                result += "    "*tab + "%s:\n%s" % (k,generate_dbg(data[k],tab+1))
            elif isinstance(data[k], (set)):
                result += "    "*tab + "%s:\n%s" % (k,generate_dbg(list(data[k]),tab+1))
            else:
                result += "    "*tab + "%s: <TODO>\n%s" % (k,generate_dbg({"type":`type(data[k])`,"str":`data[k]`},tab+1))
        return result            

# ============================
# Self test: decompile a label
# ============================

label _LB_test_screen:
    $ x = 1

init 9999 python:
    def self_test():
        if  not hasattr(renpy,"game"):
            return False, "Cannot find 'game' in renpy"
        if  not hasattr(renpy.game,"script"):
            return False, "Cannot find 'script' in renpy.game"
        if  not hasattr(renpy.game.script,"namemap"):
            return False, "Cannot find 'namemap' in renpy.game.script"
        if  type(renpy.game.script.namemap) != types.DictType:
            return False, "Not a dictionary " + ": renpy.game.script.namemap is " + `type(renpy.game.script.namemap)`
        if  not "_LB_test_screen" in renpy.game.script.namemap:
            return False, "Cannot find test label in renpy.game.script.namemap"
        if  len(renpy.game.script.namemap["_LB_test_screen"].get_children()) != 1:
            return False, "Wrong number of children of test label"
        item = renpy.game.script.namemap["_LB_test_screen"].get_children()[0]

        if  not hasattr(renpy, "ast"):
            return False, "Cannot find 'ast' in renpy"
        if  not hasattr(renpy.ast, "Python"):
            return False, "Cannot find 'Python' in renpy.ast"
        if  not isinstance(item,renpy.ast.Python):
            return False, "Wrong type of parsed python line"
        if  not hasattr(item, "code"):
            return False, "Cannot find 'code' in renpy.ast.Python"
        if  not hasattr(item.code, "source"):
            return False, "Cannot find 'source' in renpy.ast.Python.code"
        if  item.code.source is None:
            return False, "Empty source code! Have you patched RenPy already?"
        if  item.code.source != "x = 1":
            return False, "Wrong source code: " + `item.code.source`
        return True, "OK"

# =====================================
# Main code: usage of defined functions
# =====================================

init 9999 python:
    import os
    import urllib2
    import shutil

    if  _LB_SELFTEST_:
        res, msg = self_test()
        if  not res:
            renpy.error(msg)

    data = collect_rpy()   

    if  not os.path.exists(_LB_OUTPUT_DIR + os.sep + "js"):
        os.makedirs(_LB_OUTPUT_DIR + os.sep + "js")
    if  not os.path.exists(_LB_OUTPUT_DIR + os.sep + "js" + os.sep + "WebStoryEngine.js"):
        with open(_LB_OUTPUT_DIR + os.sep + "js" + os.sep + "WebStoryEngine.js", "wb") as wse:
            wse.write(urllib2.urlopen('http://cf.ichan.ru/wse/WebStoryEngine.js').read())

    if  not os.path.exists(_LB_OUTPUT_DIR + os.sep + "common"):
        os.makedirs(_LB_OUTPUT_DIR + os.sep + "common")
    for fname in ["DejaVuSans.ttf", "DejaVuSans.txt"]:
        shutil.copy2(
                renpy.config.renpy_base + os.sep + "renpy" + os.sep + "common" + os.sep + fname,
                _LB_OUTPUT_DIR + os.sep + "common" + os.sep + fname
            )

    for fname in renpy.list_files():
        new_fname = _LB_OUTPUT_DIR + os.sep + "game" + os.sep + fname
        dirname = os.path.dirname(new_fname)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        if not os.path.exists(new_fname):
            with open(new_fname, "wb") as new:
                with renpy.file(fname) as orig:
                    shutil.copyfileobj(orig, new)

    if  _LB_DEBUG_FILE_:
        with open(_LB_OUTPUT_DIR+os.sep+"dump.dbg","w") as f:
            f.write(generate_dbg(data).encode("UTF-8"))

    with open(_LB_OUTPUT_DIR+os.sep+"game.xml","w") as f:
        f.write(generate_xml(data).encode("UTF-8"))

    if  data["window_icon"]:
        import pygame
        icon = im.Image(data["window_icon"]).load()
        icon = pygame.transform.smoothscale(icon, (64,64))
        pygame.image.save(icon,_LB_OUTPUT_DIR+os.sep+"favicon.png")

    with open(_LB_OUTPUT_DIR+os.sep+"index.html","w") as f:
        f.write(codecs.BOM_UTF8+generate_html(data).encode("UTF-8"))

# ========================================================
# small compat code, for 6.15.x scripts to work with 6.x.x
# ========================================================
init -1000 python:
    class _LB_BuildLol(object):
        def __getattr__(self, name):        return lambda *args: None
        def __setattr__(self, name, value): pass
    if  not 'build' in renpy.store.__dict__:
        build = _LB_BuildLol()
