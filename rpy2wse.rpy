# RenPy to WebStoryEngine proof-of-concept converter v0.1
# Very simple code for converting most commonly used code structures
# Useful for very simple VNs like "The questions" only!

# ========
# CONTACTS
# ========
# Copyleft by lolbot, member of IIchan.ru eroge project.
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

# ==================
# HERE GOES THE CODE
# ==================

init 9999 python:

    def collect_rpy():
        data = {}

        # stage
        data["window_title"] = config.window_title
        data["screen_width"] = config.screen_width
        data["screen_height"] = config.screen_height

        # triggers
        data["keymap"] = [ ["savegames","ESCAPE"], ["next","RIGHT_ARROW"], ["next","ENTER"], ["next","SPACE"] ] 

        # textbox
        # TODO 
        data["textbox_left"] = 0
        data["textbox_right"] = 0
        data["textbox_top"] = 0
        data["textbox_bottom"] = 0
        data["textbox_yminimum"] = 125

        # characters
        sd = renpy.store.__dict__
        data["characters"] = [{"name":i,"mode":sd[i].mode,"displayname":sd[i].name} for i in sd if isinstance(sd[i], renpy.character.ADVCharacter)]

        # images
        data["images_all"] = renpy.display.image.images
        data["images_simple"] = dict([(i,img) for i,img in data["images_all"].iteritems() if isinstance(img, renpy.display.im.Image)])
        data["images_simple_packs"] = list(set([i[0] for i in data["images_simple"]]))
        data["images_solid"]  = dict([(i,img.color) for i,img in data["images_all"].iteritems() if isinstance(img, renpy.display.imagelike.Solid)])
        data["images_packs"] = list(set(data["images_simple_packs"]+[i[0] for i in data["images_solid"]]))
        data["images_ignore"] = dict([(i,img) for i,img in data["images_all"].iteritems() if isinstance(img, renpy.text.extras.ParameterizedText)])

        data["sound"] = {}
        data["sound_todo"] = []
        data["branches"] = {}
        for key,value in renpy.game.script.namemap.iteritems():
            if  isinstance(key,unicode) and not key.startswith("_") and not key.endswith("_screen"):
                collect_rpy_branch(key, value.get_children(), data)

        return data

    def collect_rpy_branch(name,cmds,data):
        data["branches"][name] = parse_rpy_branch(name,cmds,data)

    def parse_rpy_branch(name,cmds,data):
        result = []
        menuId = 0
        for i in cmds:
            if  hasattr(renpy.ast, "Say") and isinstance(i,renpy.ast.Say):
                result += [ {"type":"say","who":i.who,"what":i.what} ]

            elif  hasattr(renpy.ast, "UserStatement") and isinstance(i,renpy.ast.UserStatement):
                cmd = i.line.split(" ")
                if  cmd[0] == "play":
                    if  len(cmd) == 3 and ( (cmd[2][0] == '"' and cmd[2][-1] == '"' and not '"' in cmd[2][1:-1]) or (cmd[2][0] == "'" and cmd[2][-1] == "'" and not "'" in cmd[2][1:-1]) ):
                        if  not cmd[1] in data["sound"]:
                            data["sound"][cmd[1]] = []
                        if  not cmd[2][1:-1] in data["sound"][cmd[1]]:
                            fname = cmd[2][1:-1]
                            data["sound"][cmd[1]] += [fname]
                            title = ".".join(fname.split(".")[:-1])
                            result += [{"type":"play","channel":cmd[1],"title":title}]
                    else:
                        data["sound_todo"] += [ i.line ]
                        result += [ {"type":"todo","details":"UserStatement : "+i.line} ]
                else:
                    result += [ {"type":"todo","details":"UserStatement : "+i.line} ]

            elif  hasattr(renpy.ast, "Translate") and isinstance(i,renpy.ast.Translate):
                result += parse_rpy_branch(name,i.block,data)
            elif  hasattr(renpy.ast, "EndTranslate") and isinstance(i,renpy.ast.EndTranslate):
                pass

            elif  hasattr(renpy.ast, "Menu") and isinstance(i,renpy.ast.Menu):
                items = []
                todo = []
                for (optionId,(label, condition, block)) in enumerate(i.items):
                    if  condition == "True":
                        if  len(block) == 1 and isinstance(block[0],renpy.ast.Jump) and not block[0].expression:
                            items += [ (label, block[0].target) ]
                        else:
                            menu_label = "%s_%d_%d" % (name, menuId, optionId)
                            collect_rpy_branch(menu_label,block,data)
                            todo += [ (label, menu_label ) ]
                    else:
                        todo += [ (label, condition ) ]
                result += [ {"type":"menu","items":items,"todo":todo} ]
                menuId += 1

            elif  hasattr(renpy.ast, "Jump") and isinstance(i,renpy.ast.Jump):
                if  not i.expression:
                    result += [ {"type":"jump","target":i.target} ]
                else:
                    result += [ {"type":"todo","details":"jump expression: "+i.target} ]
                break
            elif  hasattr(renpy.ast, "Return") and isinstance(i,renpy.ast.Return):
                break

            elif  (hasattr(renpy.ast, "Scene") and isinstance(i,renpy.ast.Scene)) or (hasattr(renpy.ast, "Show") and isinstance(i,renpy.ast.Show)) or (hasattr(renpy.ast, "Hide") and isinstance(i,renpy.ast.Hide)):
                zorder = 0
                expression = None
                tag = None
                behind = []
                if len(i.imspec) == 3:
                    name, at_list, layer = i.imspec
                elif len(i.imspec) == 6:
                    name, expression, tag, at_list, layer, zorder = i.imspec
                elif len(i.imspec) == 7:
                    name, expression, tag, at_list, layer, zorder, behind = i.imspec
                if  not expression:
                    t = "scene" if isinstance(i,renpy.ast.Scene) else "show" if isinstance(i,renpy.ast.Show) else "hide"
                    result += [ {"type":t,"asset":name[0],"image":" ".join(name[1:])} ]
                else:
                    result += [ {"type":"todo","details":"show expression: "+expression} ]

            else:
                result += [ {"type":"todo","details":"unknown command: "+`type(i)`} ]
        return result

    def generate_html(data):
        result =  """<!DOCTYPE html>\n<html>\n    <head>\n        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n"""
        result += """        <title>%s</title>\n""" % data["window_title"]
        result += """        <link rel="stylesheet" href="styles/default.css" type="text/css" />\n    </head>\n"""
        result += """    <body>\n        <script src="js/WebStoryEngine.js"></script>\n        <script>\n"""
        result += """            var game = new WSE.Game({ url: "game.xml", host: typeof HOST === "undefined" ? false : HOST });\n"""
        result += """            game.start();\n        </script>\n    </body>\n</html>"""
        return result.encode("UTF-8")
    
    def generate_xml(data):
        result =  """<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n<ws>\n"""
        result += """     <settings>\n"""

        #<settings><stage>
        width, height = data["screen_width"], data["screen_height"]
        result += """        <stage width="%dpx" height="%dpx" id="Stage" create="yes" center="yes" />\n""" % (width, height)

        #<settings><triggers>
        result += """        <triggers>\n"""
        for fn, key in data["keymap"]:
            if  fn in [ "next" ]:
                result += """            <trigger event="keyup" special="%s" name="%s_by_%s" key="%s" />\n""" % ( fn, fn, key.lower(), key )
            else:
                result += """            <trigger event="keyup" function="%s" name="%s_by_%s" key="%s" />\n""" % ( fn, fn, key.lower(), key )
        result += """        </triggers>\n"""

        result += """    </settings>\n"""
        result += """    <assets>\n"""

        #<assets><textbox>
        left, right = data["textbox_left"], data["textbox_right"]
        top, bottom = data["textbox_top"], data["textbox_bottom"]
        sizes = (left, height-data["textbox_yminimum"]-bottom, width-left-right, data["textbox_yminimum"])
        result += """        <textbox name="tb_adv" behaviour="adv" cssid="tb_adv" x="%dpx" y="%dpx" width="%dpx" height="%dpx">\n""" % sizes
        result += """            <nameTemplate>{name}<br /></nameTemplate>\n        </textbox>\n""" 
        sizes = (left, top, width-left-right, height-top-bottom)
        result += """        <textbox name="tb_nvl" behaviour="nvl" cssid="tb_nvl" x="%dpx" y="%dpx" width="%dpx" height="%dpx">\n""" % sizes
        result += """            <nameTemplate>{name}<br /></nameTemplate>\n        </textbox>\n""" 

        #<assets><character>
        for c in data["characters"]:
            result += """        <character name="%s" textbox="%s">""" % (c["name"], "tb_adv" if c["mode"] == "say" else "tb_nvl")
            if  c["displayname"] != None:
                result += """<displayname>%s</displayname>""" % c["displayname"]
            result += """</character>\n"""

        #<assets><imagepack>
        #<assets><curtain>
        for i in data["images_simple_packs"]:
            result += """        <imagepack name="%s">\n""" % i
            for name, img in data["images_simple"].iteritems():
                if  name[0] == i:
                    result += """            <image name="%s" src="%s" />\n""" % (" ".join(name[1:]), "game/"+img.filename)
            result += """        </imagepack>\n"""
        for i, clr in data["images_solid"].iteritems():
            result += """        <curtain name="%s" color="rgba(%d,%d,%d,%.2f)" />\n""" % (" ".join(i), clr[0], clr[1], clr[2], clr[3]/255.0)
        for i in data["images_all"]:
            if not i in data["images_simple"].keys() + data["images_solid"].keys() + data["images_ignore"].keys():
                result += """        <!-- [TODO] Not a simple image: %s = %s -->\n""" % (" ".join(i),`img_dict[i]`)

        #<assets><audio>
        for channel, sounds in data["sound"].iteritems():
            result += """        <audio name="%s" loop="%s" fade="false">\n""" % (channel, "true" if channel in ["music"] else "false")
            for i in sounds:
                title, ext = ".".join(i.split(".")[:-1]), i.split(".")[-1]
                result += """            <track title="%s">\n""" % title
                for e in ["mp3","ogg"]:
                    if ext != e:
                        result += """                <!-- [TODO] convert "game/%s" to "game/%s.%s" -->\n""" % (i,title,e)
                    result += """                <source href="game/%s.%s" type="%s" />\n""" % (title,e,e)
                result += """            </track>\n"""
            result += """        </audio>\n"""
        for line in data["sound_todo"]:
            result += """        <!-- [TODO] Not a simple play: %s -->\n""" % line
        
        result += """    </assets>\n"""
        result += """    <scenes>\n"""

        #<scenes><scene id="start">
        result += """        <scene id="start">\n"""
        for fn, key in data["keymap"]:
            result += """            <trigger name="%s_by_%s" action="activate" />\n""" % ( fn, key.lower() )
        for im in data["images_packs"]:
            result += """            <var action="set" name="is_%s_visible" value="false" />\n""" % (im)
        result += """            <goto scene="menu" />\n        </scene>\n"""

        #<scenes><scene id="menu">
        result += """        <scene id="menu">\n            <choice>\n"""
        result += """                <option label="Start Game" scene="game" />\n"""
        result += """                <option label="Load Game" scene="saveload" />\n"""
        result += """            </choice>\n            <goto scene="menu" />\n        </scene>\n"""

        #<scenes><scene id="saveload">
        result += """        <scene id="saveload">\n            <fn name="savegames" />\n            <goto scene="menu" />\n        </scene>\n"""

        #<scenes><scene id="game">
        result += """        <scene id="game">\n            <show asset="tb_adv" effect="slide" direction="top" duration="2000"/>\n"""
        result += """            <sub scene="rpy_start" />\n"""
        for fn, key in data["keymap"]:
            result += """            <trigger name="%s_by_%s" action="deactivate" />\n""" % ( fn, key.lower() )
        result += """            <hide asset="tb_adv" effect="slide" direction="bottom" duration="2000" />\n"""
        result += """            <wait />\n            <restart/>\n        </scene>\n"""

        for key, value in data["branches"].iteritems():
            result += """        <scene id="rpy_%s">\n""" % key
            for i in value:
                if  i["type"] == "say":
                    result += """            <line s="%s">%s</line>\n""" % (i["who"] if i["who"] is not None else "narrator", i["what"])
                elif i["type"] == "play":
                    result += """            <set asset="%s" track="%s" />\n""" % (i["channel"],i["title"])
                    result += """            <play asset="%s" />\n""" % (i["channel"])
                elif i["type"] == "jump":
                    result += """            <goto scene="rpy_%s" />\n""" % (i["target"])
                elif i["type"] == "menu":
                    result += """            <choice>\n"""
                    for (label, target) in i["items"]:
                        result += """                <option label="%s" scene="rpy_%s" />\n""" % (label, target)
                    for (label, details) in i["todo"]:
                        result += """                <!-- [TODO] option label="%s" : %s -->\n""" % (label, details)
                    result += """            </choice>\n"""
                elif i["type"] == "scene":
                    for im in data["images_packs"]:
                        if  im !=  i["asset"]:
                            result += """            <hide asset="%s" ifvar="is_%s_visible" ifvalue="true" duration="0" />\n""" % (im,im)
                            result += """            <var action="set" name="is_%s_visible" value="false" />\n""" % (im)
                    result += """            <set asset="%s" image="%s" duration="0" />\n""" % (i["asset"],i["image"])
                    result += """            <show asset="%s" ifvar="is_%s_visible" ifvalue="false" duration="0" />\n""" % (i["asset"],i["asset"])
                    result += """            <var action="set" name="is_%s_visible" value="true" />\n""" % (i["asset"])
                elif i["type"] == "show":
                    result += """            <set asset="%s" image="%s" duration="0" />\n""" % (i["asset"],i["image"])
                    result += """            <show asset="%s" ifvar="is_%s_visible" ifvalue="false" duration="0" />\n""" % (i["asset"],i["asset"])
                    result += """            <var action="set" name="is_%s_visible" value="true" />\n""" % (i["asset"])
                elif i["type"] == "hide":
                    result += """            <hide asset="%s" ifvar="is_%s_visible" ifvalue="true" duration="0" />\n""" % (i["asset"],i["asset"])
                    result += """            <var action="set" name="is_%s_visible" value="false" />\n""" % (i["asset"])
                elif i["type"] == "todo":
                    result += """            <!-- [TODO] %s -->\n""" % i["details"]
                else:
                    renpy.error(i)
            result += """        </scene>\n"""

        result += """    </scenes>\n"""
        result += """</ws>"""

        return result.encode("UTF-8")

    data = collect_rpy()   

    with open("game.xml","w") as f:
        f.write(generate_xml(data))

    with open("index.html","w") as f:
        f.write(generate_html(data))
