import json
import math

def calculate_time(text):
    return math.ceil(1.2 + (len(text) * 0.1))

import json
import math

def calculate_time(text):
    return math.ceil(1.2 + (len(text) * 0.1))

# 核心邏輯：只負責把 JSON 字典轉成 SQF 字串
def generate_sqf_string(data):
    nid = data.get("npc_id", "hero")
    npc_name = data["npc_name"]
    action_text = data["action"]
    opening_text = data["opening"]
    opening_time = calculate_time(opening_text)
    
    menu_items = []
    cases_sqf = ""
    
    for i, opt in enumerate(data['options']):
        title = opt['title']
        auto_case_id = f"opt_{i}"
        end_act = opt['end_action']
        
        menu_items.append(f'                ["{title}", [{i+2}], "", -5, [["expression", "[\'{auto_case_id}\'] spawn fnc_selectDialogueOption_{nid}"]], "1", "1"]')
        
        case_body = f'        case "{auto_case_id}": {{\n'
        for line in opt['dialogue']:
            who_key, text = line[0], line[1]
            who = "player" if who_key == "player" else f"currentHero_{nid}"
            label = "name player" if who_key == "player" else f'"{npc_name}"'
            dur = calculate_time(text)
            case_body += f'            [{who}, {label}, "{text}", {dur}] call fnc_showHeroSubtitle_{nid};\n'
            case_body += f'            sleep {dur};\n'
            case_body += f'            if (!dialogueMenuActive_{nid}) exitWith {{}};\n'
        
        if end_act == "loop":
            case_body += f'            (currentHero_{nid}) setVariable ["isTalking", false, true];\n'
            case_body += f'            [player, currentHero_{nid}] call fnc_initiateDialogue_{nid};\n'
        else:
            case_body += f'            dialogueMenuActive_{nid} = false;\n'
            case_body += f'            (currentHero_{nid}) setVariable ["isTalking", false, true];\n'
            case_body += f'            isFirstInteraction_{nid} = true;\n'
        case_body += "        };\n"
        cases_sqf += case_body

    menu_str = ",\n".join(menu_items)

    return f"""
isFirstInteraction_{nid} = true;
dialogueMenuActive_{nid} = false;

if (isNil "fnc_getSideColor") then {{
    fnc_getSideColor = {{
        params ["_npc"];
        private _side = side _npc;
        private _color = "#FFFFFF";
        switch (_side) do {{
            case west: {{ _color = "#0066CC"; }};
            case east: {{ _color = "#990000"; }};
            case resistance: {{ _color = "#007F00"; }};
            case civilian: {{ _color = "#66007f"; }};
        }};
        _color
    }};
}};

fnc_showHeroSubtitle_{nid} = {{
    params ["_npc", "_name", "_text", ["_duration", 3]];
    private _color = [_npc] call fnc_getSideColor;
    private _formattedText = format ["<t align='center' size='0.6' font='PuristaBold' shadow='2'><t color='%1'>%2:</t> <t color='#FFFFFF'>%3</t></t>", _color, _name, _text];
    private _nearbyPlayers = allPlayers select {{ _x distance _npc < 5 }};
    if (count _nearbyPlayers > 0) then {{
        [_formattedText, 0, 1, _duration, 0, 0] remoteExec ["BIS_fnc_dynamicText", _nearbyPlayers];
    }};
}};

fnc_initiateDialogue_{nid} = {{
    params ["_player", "_npc"];
    if !(_npc getVariable ["isTalking", false]) then {{
        _npc setVariable ["isTalking", true, true];
        dialogueMenuActive_{nid} = true;
        currentHero_{nid} = _npc;
        [] spawn {{
            if (isFirstInteraction_{nid}) then {{
                sleep 0.1;
                [currentHero_{nid}, "{npc_name}", "{opening_text}", {opening_time}] call fnc_showHeroSubtitle_{nid};
                sleep {opening_time};
                isFirstInteraction_{nid} = false;
            }};
            if (!dialogueMenuActive_{nid}) exitWith {{}};
            _dialogueMenu = [
                ["{action_text}", true],
{menu_str}
            ];
            showCommandingMenu "#USER:_dialogueMenu";
        }};
        [] spawn {{
            while {{dialogueMenuActive_{nid}}} do {{
                if (player distance currentHero_{nid} > 5) exitWith {{
                    showCommandingMenu "";
                    titleText ["<t color='#ff0000' size='1.2'>距離過遠，對話中斷</t>","PLAIN DOWN",0.5,true,true];
                    dialogueMenuActive_{nid} = false;
                    (currentHero_{nid}) setVariable ["isTalking", false, true];
                    isFirstInteraction_{nid} = true;
                }};
                sleep 0.5;
            }};
        }};
    }};
}};

fnc_selectDialogueOption_{nid} = {{
    params ["_option"];
    showCommandingMenu ""; 
    sleep 0.02;
    switch (_option) do {{
{cases_sqf}    }};
}};

_npcHero = _this;
_npcHero setVariable ["isTalking", false, true];
_npcHero addAction ["<t color='#FFFF00'>{action_text}</t>", {{
    params ["_target", "_caller"];
    if !(_target getVariable ["isTalking", false]) then {{
        [_caller, _target] call fnc_initiateDialogue_{nid};
    }} else {{
        titleText ["<t color='#ff0000' size='1.2'>對方正在對話中</t>","PLAIN DOWN",0.5,true,true];
    }};
}}, nil, 1.5, true, true, "", "player distance _target <= 3"];
"""

def build_and_export_sqf(json_input_file, output_file):
    with open(json_input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    content = generate_sqf_string(data)
    with open(output_file, 'w', encoding='utf-8') as out_f:
        out_f.write(content)
    print("done")

if __name__ == "__main__":
    build_and_export_sqf('input/input.json', 'output/output.sqf')