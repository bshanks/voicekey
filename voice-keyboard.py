#!/usr/bin/env python

global VOICE_KEYBOARD_RES_PATH, ACOUSTIC_MODEL_PATH, MICROPHONE_DEVICE, MLLR_ARGS, VOICE_KEYBOARD_LOG_PATH

VOICE_KEYBOARD_RES_PATH = '/home/bshanks/prog/speech/voice-keyboard'
ACOUSTIC_MODEL_PATH = '/home/bshanks/prog/speech/wsj_all_cont_3no_4000_32'
MICROPHONE_DEVICE_PATH = '/dev/dsp0'
MLLR_ARGS = ''
VOICE_KEYBOARD_LOG_PATH = ''
XDOTOOL_PATH = '/usr/bin/xdotool'
WMCTRL_PATH = '/usr/bin/wmctrl'
FAKEKEY_UINPUT_PATH = '/home/bshanks/prog/speech/voice-keyboard/fakekey_uinput'
LAUNCH_TERMINAL_PATH = '/usr/bin/xterm'
#VIRTUAL_KEYBOARD_PROGRAM = 'FAKEKEY_UINPUT'  # alternately, 'XDOTOOL'
VIRTUAL_KEYBOARD_PROGRAM = 'XDOTOOL'  # alternately, 'XDOTOOL'

# copyright 2008 bayle shanks. released under the GPL, version 3 or later.

MICROPHONE_DEVICE_PATH = '/dev/dsp1'
MLLR_ARGS = '-mllr /home/bshanks/prog/speech/mllr_matrix-current'
VOICE_KEYBOARD_LOG_PATH = '/home/bshanks/prog/speech/voice-keyboard-log.hyp'
FAKEKEY_UINPUT_PATH = '/home/bshanks/prog/speech/voice-keyboard/fakekey_uinput'
WMCTRL_PATH = '/usr/bin/wmctrl'

#DICTATION_MODE_SPHINX_CMD = 'sphinx3_livesegment -alpha .82 -hmm /home/bshanks/prog/speech/wsj_all_cont_3no_4000_32 -fdict  /home/bshanks/prog/speech/lm_giga_5k_nvp_3gram/lm_giga_5k_nvp.sphinx.filler -feat       s3_1x39 -lmctlfn lmctl -dict voice-keyboard-current.dic -hyp /tmp/voice-keyboard-current.hyp  -mllr /home/bshanks/prog/speech/mllr_matrix-current -mixw /home/bshanks/prog/speech/wsj_all_cont_3no_4000_32/mixture_weights -mean /home/bshanks/prog/speech/wsj_all_cont_3no_4000_32/means -var /home/bshanks/prog/speech/wsj_all_cont_3no_4000_32/variances -beam 1e-70 -pbeam 1e-70 -wend_beam 1e-85 -maxhistpf 125 -maxhmmpf 25000  -adcdev /dev/dsp1 -beam 1e-80 -wbeam 1e-60 -maxhmmpf 2500 -maxcdsenpf 1500 -adcdev /dev/dsp1 -subvq /home/bshanks/prog/speech/wsj_all_cont_3no_4000_32/subvq -subvqbeam 1e-2'

#print DICTATION_MODE_SPHINX_CMD


#import sys
#sys.exit() 


# usage: killall sphinx3_livesegment; ./voice-keyboard.py
from string import Template
import os
#from os import *
from re import *
from subprocess import *
from time import *
import wx
from threading import *
import sys
import string

global lastCmd, repeatCmd, modifierList, status, mode, spacer, lastUttId, sphinx_subprocess, DICTATION_MODE_SPHINX_CMD, HYP_PATH, HYP_LOG, cmdWords, otherKeypressWords, asciiKeypressWords, numberWords, modifierWords,sphinx_config, DICTATION_HYP_PATH, KEYBOARD_HYP_PATH, waitingForVoiceCmd, parentFrame, stoppedStatus, sphinx_cmd

SPHINX_CMD_TEMPLATE = 'sphinx3_livesegment -alpha .82 -hmm $ACOUSTIC_MODEL_PATH -fdict $VOICE_KEYBOARD_RES_PATH/voice-keyboard.filler -feat       s3_1x39 -lmctlfn $VOICE_KEYBOARD_RES_PATH/lmctl -dict $VOICE_KEYBOARD_RES_PATH/voice-keyboard-current.dic -hyp /tmp/voice-keyboard-current.hyp $MLLR_ARGS -mixw $ACOUSTIC_MODEL_PATH/mixture_weights -mean $ACOUSTIC_MODEL_PATH/means -var $ACOUSTIC_MODEL_PATH/variances -beam 1e-70 -pbeam 1e-70 -wend_beam 1e-85 -maxhistpf 125 -maxhmmpf 25000  -adcdev $MICROPHONE_DEVICE_PATH -beam 1e-80 -wbeam 1e-60 -maxhmmpf 2500 -maxcdsenpf 1500 -subvq $ACOUSTIC_MODEL_PATH/subvq -subvqbeam 1e-2 -samprate 11025'

sphinx_cmd = Template(SPHINX_CMD_TEMPLATE).substitute(locals())

DICTATION_HYP_PATH = '/tmp/voice-keyboard-current.hyp'
KEYBOARD_HYP_PATH = '/tmp/voice-keyboard-keyboard.hyp'
HYP_PATH = DICTATION_HYP_PATH

sphinx_config = { 'hmm' : '/usr/local/share/pocketsphinx/model/hmm/wsj1',
                  'lm' : 'voice-keyboard-current.lm',
                  'dict' : 'voice-keyboard-current.dic',
                  'live': 'yes',
                  'hyp': HYP_PATH,}


def type_word(w, spacer):
    if VIRTUAL_KEYBOARD_PROGRAM == 'FAKEKEY_UINPUT':
        for c in w.lower():
            os.spawnlp(os.P_WAIT,FAKEKEY_UINPUT_PATH, FAKEKEY_UINPUT_PATH,'-c',c)
        if spacer:
            os.spawnlp(os.P_WAIT,FAKEKEY_UINPUT_PATH, FAKEKEY_UINPUT_PATH, '-c',spacer)
    elif VIRTUAL_KEYBOARD_PROGRAM == 'XDOTOOL':
        #os.spawnlp(os.P_WAIT,XDOTOOL_PATH, XDOTOOL_PATH,'type',w.lower() + spacer)
        # bug in xdotool with modified keyboard layouts: http://code.google.com/p/semicomplete/issues/detail?id=13
        for key in (w.lower()):
            os.spawnlp(os.P_WAIT,XDOTOOL_PATH, XDOTOOL_PATH,'key',key)
        if spacer == ' ':
            os.spawnlp(os.P_WAIT,XDOTOOL_PATH, XDOTOOL_PATH,'key', 'space')
        if spacer == '_':
            os.spawnlp(os.P_WAIT,XDOTOOL_PATH, XDOTOOL_PATH,'key', 'underscore')



modifierWords_FAKEKEY_UINPUT = {
    'CONTROL' : ['-k', '29'],
    'ALTERNATE' : ['-k', '56'],
    'SUPER' : ['-k', '125'],
    'HYPER' : ['-k', '126'],
    'SHIFT' : ['-k', '42'],
}

modifierWords_XDOTOOL = {
    'CONTROL' : ['Control'],
    'ALTERNATE' : ['Alt'],
    'SUPER' : ['Super'],
    'HYPER' : ['Hyper'],
    'SHIFT' : ['Shift'],
}

numberWords_FAKEKEY_UINPUT = {
    'ZERO' : 0,
    'ONE' : 1,
    'TWO' : 2,
    'THREE' : 3,
    'FOUR' : 4,
    'FIVE' : 5,
    'SIX' : 6,
    'SEVEN' : 7,
    'EIGHT' : 8,
    'NINE' : 9,
}


numberWords_XDOTOOL = {
    'ZERO' : 0,
    'ONE' : 1,
    'TWO' : 2,
    'THREE' : 3,
    'FOUR' : 4,
    'FIVE' : 5,
    'SIX' : 6,
    'SEVEN' : 7,
    'EIGHT' : 8,
    'NINE' : 9,
}



asciiKeypressWords_FAKEKEY_UINPUT = {
    'ALFA' : 'a',
#    'A' : 'a',
    'BRAVO' : 'b',
    'CHARLIE' : 'c',
    'DELTA' : 'd',
    'ECHO' : 'e',
    'FOXTROT' : 'f',
    'GINGER' : 'g',
    'HENRY' : 'h',
    'INDIA' : 'i',
#    'I' : 'i',
    'JULIET' : 'j',
    'KILO' : 'k',
    'LIMA' : 'l',
    'MICHAEL' : 'm',
    'NOVEMBER' : 'n',
    'OSCAR' : 'o',
    'PETER' : 'p',
    'QUEBEC' : 'q',
    'ROBBIE' : 'r',
    'SIERRA' : 's',
    'TANGO' : 't',
    'UNIFORM' : 'u',
    'VICTOR' : 'v',
    'WHISKEY' : 'w',
    'X-RAY' : 'x',
    'YANKEE' : 'y',
    'ZULU' : 'z',
    'APOSTROPHE' : '\'',
    'ENTER_KEY' : '\r',
    'ZERO' : '0',
    'ONE' : '1',
    'TWO' : '2',
    'THREE' : '3',
    'FOUR' : '4',
    'FIVE' : '5',
    'SIX' : '6',
    'SEVEN' : '7',
    'EIGHT' : '8',
    'NINE' : '9',
    'ESCAPE_KEY' : '\x1b',
    'TABULAR' : '\t',
    'BRAY' : ' ',
    'BACKTICK' : '`',
    'QUOTATION' : '\"',
    'SLASH' : '/',
    'COMMA' : ',',
    'COLON' : ':',
    'SEMICOLON' : ';',
    'NUMBER_SIGN' : '#',
    'PERIOD' : '.',
    'BACKSLASH' : '\\',
    'AT_SIGN' : '@',
    'STAR' : '*',
    'LEFT_PARENS' : '(',
    'RIGHT_PARENS' : ')',
    'LEFT_BRACE' : '{',
    'RIGHT_BRACE' : '}',
    'DASH' : '-',
    'EQUALS' : '=',
    'PLUS' : '+',
    'AMPERSAND' : '&',
    'CIRCUMFLEX' : '^',
    'DOLLAR_SIGN' : '$',
    'PERCENT' : '%',
    'EXCLAMATION' : '!',
    'QUESTION_MARK' : '?',
    'TWIDDLE' : '~',
    'UNDERSCORE' : '_',
    'VERTICAL_BAR' : '|',
    'LEFT_BRACKET' : '[',
    'RIGHT_BRACKET' : ']',
    'GREATER_THAN_SIGN' : '>',
    'LESS_THAN_SIGN' : '<',
    'ERASE' : '\b',
}

asciiKeypressWords_XDOTOOL = {
    'ALFA' : 'a',
#    'A' : 'a',
    'BRAVO' : 'b',
    'CHARLIE' : 'c',
    'DELTA' : 'd',
    'ECHO' : 'e',
    'FOXTROT' : 'f',
    'GINGER' : 'g',
    'HENRY' : 'h',
    'INDIA' : 'i',
#    'I' : 'i',
    'JULIET' : 'j',
    'KILO' : 'k',
    'LIMA' : 'l',
    'MICHAEL' : 'm',
    'NOVEMBER' : 'n',
    'OSCAR' : 'o',
    'PETER' : 'p',
    'QUEBEC' : 'q',
    'ROBBIE' : 'r',
    'SIERRA' : 's',
    'TANGO' : 't',
    'UNIFORM' : 'u',
    'VICTOR' : 'v',
    'WHISKEY' : 'w',
    'X-RAY' : 'x',
    'YANKEE' : 'y',
    'ZULU' : 'z',
    'APOSTROPHE' : 'apostrophe',
    'ENTER_KEY' : 'Return',
    'ZERO' : '0',
    'ONE' : '1',
    'TWO' : '2',
    'THREE' : '3',
    'FOUR' : '4',
    'FIVE' : '5',
    'SIX' : '6',
    'SEVEN' : '7',
    'EIGHT' : '8',
    'NINE' : '9',
    'ESCAPE_KEY' : 'Escape',
    'TABULAR' : 'Tab',
    'BRAY' : 'space',
    'BACKTICK' : 'grave',
    'QUOTATION' : 'shift+quotedbl',
    'SLASH' : 'slash',
    'COMMA' : 'comma',
    'COLON' : 'shift+colon',
    'SEMICOLON' : 'semicolon',
    'NUMBER_SIGN' : 'shift+numbersign',
    'PERIOD' : 'period',
    'BACKSLASH' : 'backslash',
    'AT_SIGN' : 'shift+at',
    'STAR' : 'shift+asterisk',
    'LEFT_PARENS' : 'shift+parenleft',
    'RIGHT_PARENS' : 'shift+parenright',
    'LEFT_BRACE' : 'shift+braceleft',
    'RIGHT_BRACE' : 'shift+braceright',
    'DASH' : 'minus',
    'EQUALS' : 'equal',
    'PLUS' : 'shift+plus',
    'AMPERSAND' : 'shift+ampersand',
    'CIRCUMFLEX' : 'shift+asciicircum',
    'DOLLAR_SIGN' : 'shift+dollar',
    'PERCENT' : 'shift+percent',
    'EXCLAMATION' : 'shift+exclam',
    'QUESTION_MARK' : 'shift+question',
    'TWIDDLE' : 'shift+asciitilde',
    'UNDERSCORE' : 'shift+underscore',
    'VERTICAL_BAR' : 'shift+bar',
    'LEFT_BRACKET' : 'bracketleft',
    'RIGHT_BRACKET' : 'bracketright',
    'GREATER_THAN_SIGN' : 'shift+greater',
    'LESS_THAN_SIGN' : 'less',
    'ERASE' : 'BackSpace',
}


otherKeypressWords_FAKEKEY_UINPUT = {
        'UP_ARROW' : '103',
    'DOWN_ARROW' : '108',
    'LEFT_ARROW' : '105',
    'RIGHT_ARROW' : '106',
    'NORTH_ARROW' : '103',
    'SOUTH_ARROW' : '108',
    'WEST_ARROW' : '105',
    'EAST_ARROW' : '106',
    'PAGE_DOWN' : '109',
    'PAGE_UP' : '104',
    'HOME_KEY' : '102',
    'END_KEY' : '107',
    'INSERT' : '110',
    'DELETE' : '111',
    'FUNCTION_KEY_1' : '59',
    'FUNCTION_KEY_2' : '60',
    'FUNCTION_KEY_3' : '61',
    'FUNCTION_KEY_4' : '62',
    'FUNCTION_KEY_5' : '63',
    'FUNCTION_KEY_6' : '64',
    'FUNCTION_KEY_7' : '65',
    'FUNCTION_KEY_8' : '66',
    'FUNCTION_KEY_9' : '67',
    'FUNCTION_KEY_TEN' : '68',
    'FUNCTION_KEY_ELEVEN' : '87',
    'FUNCTION_KEY_TWELVE' : '88',
    'FUNCTION_KEY_THIRTEEN' : '183',
    'FUNCTION_KEY_FOURTEEN' : '184',
    'FUNCTION_KEY_FIFTEEN' : '185',
    'FUNCTION_KEY_SIXTEEN' : '186',
    'FUNCTION_KEY_SEVENTEEN' : '187',
    'FUNCTION_KEY_EIGHTEEN' : '188',
    'FUNCTION_KEY_NINETEEN' : '189',
    'FUNCTION_KEY_TWENTY' : '190',
    'FUNCTION_KEY_TWENTY_ONE' : '191',
    'FUNCTION_KEY_TWENTY_TWO' : '192',
    'FUNCTION_KEY_TWENTY_THREE' : '193',
    'FUNCTION_KEY_TWENTY_FOUR' : '194',

    'CUT_COMMAND' : '137',
    'COPY_COMMAND' : '133',
    'PASTE_COMMAND' : '135',
    'UNDO_COMMAND' : '131',
    'REDO_COMMAND' : '182',
    'OPEN_COMMAND' : '134',
    'FIND_COMMAND' : '136',
        'SAVE_COMMAND' : '234',

            'PREVIOUS_COMMAND' : '191',
    'NEXT_COMMAND' : '192',
    'BACK_COMMAND' : '158',
    'FORWARD_COMMAND' : '159',
    'NEW_COMMAND' : '190',
#    'CYCLE_WINDOWS' : '154;',
        'CLOSE_COMMAND' : '193',
}

otherKeypressWords_XDOTOOL = {
    'UP_ARROW' : 'Up',
    'DOWN_ARROW' : 'Down',
    'LEFT_ARROW' : 'Left',
    'RIGHT_ARROW' : 'Right',
    'NORTH_ARROW' : 'Up',
    'SOUTH_ARROW' : 'Down',
    'WEST_ARROW' : 'Left',
    'EAST_ARROW' : 'Right',
    'PAGE_DOWN' : 'Page_Down',
    'PAGE_UP' : 'Page_Up',
    'HOME_KEY' : 'Home',
    'END_KEY' : 'End',
    'INSERT' : 'Insert',
    'DELETE' : 'Delete',
    'FUNCTION_KEY_1' : 'F1',
    'FUNCTION_KEY_2' : 'F2',
    'FUNCTION_KEY_3' : 'F3',
    'FUNCTION_KEY_4' : 'F4',
    'FUNCTION_KEY_5' : 'F5',
    'FUNCTION_KEY_6' : 'F6',
    'FUNCTION_KEY_7' : 'F7',
    'FUNCTION_KEY_8' : 'F8',
    'FUNCTION_KEY_9' : 'F9',
    'FUNCTION_KEY_TEN' : 'F10',
    'FUNCTION_KEY_ELEVEN' : 'F11',
    'FUNCTION_KEY_TWELVE' : 'F12',
    'FUNCTION_KEY_THIRTEEN' : 'F13',
    'FUNCTION_KEY_FOURTEEN' : 'F14',
    'FUNCTION_KEY_FIFTEEN' : 'F15',
    'FUNCTION_KEY_SIXTEEN' : 'F16',
    'FUNCTION_KEY_SEVENTEEN' : 'F17',
    'FUNCTION_KEY_EIGHTEEN' : 'F18',
    'FUNCTION_KEY_NINETEEN' : 'F19',
    'FUNCTION_KEY_TWENTY' : 'F20',
    'FUNCTION_KEY_TWENTY_ONE' : 'F21',
    'FUNCTION_KEY_TWENTY_TWO' : 'F22',
    'FUNCTION_KEY_TWENTY_THREE' : 'F23',
    'FUNCTION_KEY_TWENTY_FOUR' : 'F24',

    'CUT_COMMAND' : 'XF86Cut',
    'COPY_COMMAND' : 'XF86Copy',
    'PASTE_COMMAND' : 'XF86Paste',
    'UNDO_COMMAND' : 'osfUndo',
    'REDO_COMMAND' : 'UNDEFINED',
    'OPEN_COMMAND' : 'XF86Open',
    'FIND_COMMAND' : 'Find',
        'SAVE_COMMAND' : 'XF86Save',

            'PREVIOUS_COMMAND' : 'ctrl+shift+Tab',
    'NEXT_COMMAND' : 'ctrl+Tab',
    'BACK_COMMAND' : 'alt+Left',
    'FORWARD_COMMAND' : 'alt+Right',
    'NEW_COMMAND' : 'ctrl+t',
#    'CYCLE_WINDOWS' : '154;',
        'CLOSE_COMMAND' : 'ctrl+w',
}



cmdWords_that_dont_type_FAKEKEY_UINPUT = {
        'LOWER_WINDOW' : [(FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, '-k', '125','-k','108'], os.P_WAIT)],
        'CYCLE_WINDOWS' : [(FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, '-k','56','-c','\t'], os.P_WAIT)],
    'WORK_SPACE_1' : [(WMCTRL_PATH, [WMCTRL_PATH, '-s','0'], os.P_WAIT)],
    'WORK_SPACE_2' : [(WMCTRL_PATH, [WMCTRL_PATH, '-s','1'], os.P_WAIT)],
    'WORK_SPACE_3' : [(WMCTRL_PATH, [WMCTRL_PATH, '-s','2'], os.P_WAIT)],
    'WORK_SPACE_4' : [(WMCTRL_PATH, [WMCTRL_PATH, '-s','3'], os.P_WAIT)],
    'WORK_SPACE_5' : [(WMCTRL_PATH, [WMCTRL_PATH, '-s','4'], os.P_WAIT)],
    'WORK_SPACE_6' : [(WMCTRL_PATH, [WMCTRL_PATH, '-s','5'], os.P_WAIT)],
    'WORK_SPACE_7' : [(WMCTRL_PATH, [WMCTRL_PATH, '-s','6'], os.P_WAIT)],
    'WORK_SPACE_8' : [(WMCTRL_PATH, [WMCTRL_PATH, '-s','7'], os.P_WAIT)],
    'WORK_SPACE_9' : [(WMCTRL_PATH, [WMCTRL_PATH, '-s','8'], os.P_WAIT)],

    'LAUNCH_TERMINAL' : [(LAUNCH_TERMINAL_PATH, [LAUNCH_TERMINAL_PATH], os.P_NOWAIT)],

    'MISTAKE' : [],
        }

cmdWords_that_dont_type_XDOTOOL = {
        'LOWER_WINDOW' : [(XDOTOOL_PATH, [XDOTOOL_PATH, 'key', 'super+Down'], os.P_WAIT)],
        'CYCLE_WINDOWS' : [(XDOTOOL_PATH, [XDOTOOL_PATH, 'key', 'alt+Tab'], os.P_WAIT)],
    'WORK_SPACE_1' : [(WMCTRL_PATH, [WMCTRL_PATH, '-s','0'], os.P_WAIT)],
    'WORK_SPACE_2' : [(WMCTRL_PATH, [WMCTRL_PATH, '-s','1'], os.P_WAIT)],
    'WORK_SPACE_3' : [(WMCTRL_PATH, [WMCTRL_PATH, '-s','2'], os.P_WAIT)],
    'WORK_SPACE_4' : [(WMCTRL_PATH, [WMCTRL_PATH, '-s','3'], os.P_WAIT)],
    'WORK_SPACE_5' : [(WMCTRL_PATH, [WMCTRL_PATH, '-s','4'], os.P_WAIT)],
    'WORK_SPACE_6' : [(WMCTRL_PATH, [WMCTRL_PATH, '-s','5'], os.P_WAIT)],
    'WORK_SPACE_7' : [(WMCTRL_PATH, [WMCTRL_PATH, '-s','6'], os.P_WAIT)],
    'WORK_SPACE_8' : [(WMCTRL_PATH, [WMCTRL_PATH, '-s','7'], os.P_WAIT)],
    'WORK_SPACE_9' : [(WMCTRL_PATH, [WMCTRL_PATH, '-s','8'], os.P_WAIT)],

    'LAUNCH_TERMINAL' : [(LAUNCH_TERMINAL_PATH, [LAUNCH_TERMINAL_PATH], os.P_NOWAIT)],

    'MISTAKE' : [],
        }

cmdWords_that_type_FAKEKEY_UINPUT = {

    'LESS' : [(FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 'l'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 'e'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 's'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 's'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, ' '], os.P_WAIT)],
    'LIST' : [(FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 'l'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 'i'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 's'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 't'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, ' '], os.P_WAIT)],
    'CHANGE_DIRECTORY' : [(FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 'c'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 'd'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, ' '], os.P_WAIT)],
    'EDITOR' : [(FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 'e'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 'd'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 'i'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 't'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 'o'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 'r'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, ' '], os.P_WAIT)],
    'U_S_R' : [(FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 'u'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 's'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 'r'], os.P_WAIT)],
    'BIN' : [(FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 'b'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 'i'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 'n'], os.P_WAIT)],
    'ET_CETERA' : [(FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 'e'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 't'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 'c'], os.P_WAIT)],
    'X_ELEVEN' : [(FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 'X'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, '1'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, '1'], os.P_WAIT)],
        'TAR' : [(FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 't'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 'a'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, 'r'], os.P_WAIT), (FAKEKEY_UINPUT_PATH, [FAKEKEY_UINPUT_PATH, ' '], os.P_WAIT)],

    }


cmdWords_that_type_XDOTOOL = {

    'LESS' : [(XDOTOOL_PATH, [XDOTOOL_PATH, 'type', 'less '], os.P_WAIT)],
    'LIST' : [(XDOTOOL_PATH, [XDOTOOL_PATH, 'type', 'ls '], os.P_WAIT)],
    'CHANGE_DIRECTORY' : [(XDOTOOL_PATH, [XDOTOOL_PATH, 'type', 'cd '], os.P_WAIT)],
    'EDITOR' : [(XDOTOOL_PATH, [XDOTOOL_PATH, 'type', 'editor '], os.P_WAIT)],
    'U_S_R' : [(XDOTOOL_PATH, [XDOTOOL_PATH, 'type', 'usr'], os.P_WAIT)],
    'BIN' : [(XDOTOOL_PATH, [XDOTOOL_PATH, 'type', 'bin'], os.P_WAIT)],
    'ET_CETERA' : [(XDOTOOL_PATH, [XDOTOOL_PATH, 'type', 'etc'], os.P_WAIT)],
    'X_ELEVEN' : [(XDOTOOL_PATH, [XDOTOOL_PATH, 'type', 'X11'], os.P_WAIT)],
    'TAR' : [(XDOTOOL_PATH, [XDOTOOL_PATH, 'type', 'tar '], os.P_WAIT)],
    }



if VIRTUAL_KEYBOARD_PROGRAM == 'FAKEKEY_UINPUT':
    modifierWords = modifierWords_FAKEKEY_UINPUT
    numberWords = numberWords_FAKEKEY_UINPUT
    asciiKeypressWords = asciiKeypressWords_FAKEKEY_UINPUT
    otherKeypressWords = otherKeypressWords_FAKEKEY_UINPUT
    cmdWords_that_dont_type = cmdWords_that_dont_type_FAKEKEY_UINPUT
    cmdWords_that_type = cmdWords_that_type_FAKEKEY_UINPUT
elif VIRTUAL_KEYBOARD_PROGRAM == 'XDOTOOL':
    modifierWords = modifierWords_XDOTOOL
    numberWords = numberWords_XDOTOOL
    asciiKeypressWords = asciiKeypressWords_XDOTOOL
    otherKeypressWords = otherKeypressWords_XDOTOOL
    cmdWords_that_dont_type = cmdWords_that_dont_type_XDOTOOL
    cmdWords_that_type = cmdWords_that_type_XDOTOOL

cmdWords = {}
cmdWords.update(cmdWords_that_dont_type)
cmdWords.update(cmdWords_that_type)

keystrokes_and_cmdWords_that_dont_type = {}
keystrokes_and_cmdWords_that_dont_type.update(asciiKeypressWords)
keystrokes_and_cmdWords_that_dont_type.update(numberWords)
keystrokes_and_cmdWords_that_dont_type.update(modifierWords)
keystrokes_and_cmdWords_that_dont_type.update(otherKeypressWords)


#_pocketsphinx.parse_argdict(sphinx_config)
#_pocketsphinx.init()
#_pocketsphinx.begin_utt()

#os.system('pocketsphinx_continuous -hmm /usr/local/share/pocketsphinx/model/hmm/wsj1 -lm keyboard-vocab.lm -dict keyboard-vocab.dic -hyp /tmp/voice-keyboard-current-keyboard.hyp &');
#os.spawnlp(os.P_NOWAIT, 'pocketsphinx_continuous', 'pocketsphinx_continuous', '-hmm', '/usr/local/share/pocketsphinx/model/hmm/wsj1', '-lm keyboard-vocab.lm', '-dict keyboard-vocab.dic', '-hyp /tmp/voice-keyboard-current-keyboard.hyp');

try:
    os.system('cat ' + HYP_PATH + ' >> ' + VOICE_KEYBOARD_LOG_PATH)
    os.unlink(HYP_PATH)
except:
    pass


os.system('killall sphinx3_livesegment')

sphinx_subprocess = Popen(sphinx_cmd, shell=True, stdin=PIPE)

lastUttId = {}
lastUttId[DICTATION_HYP_PATH] = -1
lastUttId[KEYBOARD_HYP_PATH] = -1

lastCmd = ()
repeatCmd = ()
modifierList = []
status = "stopped"
stoppedStatus = 0;
mode = "words"
spacer = ' '
waitingForVoiceCmd=False

def pause():
    global status, stoppedStatus, parentFrame
    status = "stopped"
    stoppedStatus = 0;
    wx.PostEvent(parentFrame, StatusEvent("stopped"))
    print "hello "

def resume():
    global status, parentFrame
    status = "ready"
    wx.PostEvent(parentFrame, StatusEvent("ready"))

def keyboardMode():
    global mode, parentFrame
    
    mode = "keyboard"
    sphinx_subprocess.stdin.write("SET SILENCE_LENGTH 0.05\n")
    sphinx_subprocess.stdin.write("SET BEAM 1e-70\n")
    sphinx_subprocess.stdin.write("SET PBEAM 1e-70\n")
    sphinx_subprocess.stdin.write("SET WEND_BEAM 1e-70\n")
    sphinx_subprocess.stdin.write("SET WBEAM 1e-60\n")
    sphinx_subprocess.stdin.write("SET MAXHMMPF 2500\n")
    sphinx_subprocess.stdin.write("SET MAXCDSENPF 1500\n")
    sphinx_subprocess.stdin.write("SET MAXHISTPF 100\n")
    sphinx_subprocess.stdin.write("SET MAXWPF 20\n")
    sphinx_subprocess.stdin.write("SET SUBVQBEAM 1e-2\n")
    sphinx_subprocess.stdin.write("RESET BEAM\n")
    sphinx_subprocess.stdin.write("SET LM keyboard\n")
    wx.PostEvent(parentFrame, ModeEvent("keyboard"))

def regularMode():
    global mode, parentFrame

    mode = "words"
    #sphinx_subprocess.stdin.write("SET LM regular\n") # RESET BEAM also resets LM
    sphinx_subprocess.stdin.write("SET SILENCE_LENGTH 0.25\n")
#    sphinx_subprocess.stdin.write("SET BEAM 1e-70\n")
#    sphinx_subprocess.stdin.write("SET PBEAM 1e-50\n")
#    sphinx_subprocess.stdin.write("SET WEND_BEAM 1e-85\n")
    sphinx_subprocess.stdin.write("SET BEAM 1e-80\n")
    sphinx_subprocess.stdin.write("SET PBEAM 1e-70\n")
    sphinx_subprocess.stdin.write("SET WEND_BEAM 1e-80\n")
    sphinx_subprocess.stdin.write("SET WBEAM 1e-60\n")
    sphinx_subprocess.stdin.write("SET MAXHMMPF 15000\n")
    sphinx_subprocess.stdin.write("SET MAXCDSENPF 10000\n")
    sphinx_subprocess.stdin.write("SET MAXHISTPF 100\n")
#    sphinx_subprocess.stdin.write("SET MAXHISTPF 150\n")
    
    sphinx_subprocess.stdin.write("SET MAXWPF 20\n")
#    sphinx_subprocess.stdin.write("SET MAXWPF 40\n")
    sphinx_subprocess.stdin.write("SET SUBVQBEAM 1e-2\n")
    sphinx_subprocess.stdin.write("RESET BEAM\n")
    wx.PostEvent(parentFrame, ModeEvent("words"))

def viewMode():
    global mode, parentFrame
    
    mode = "view"
    sphinx_subprocess.stdin.write("SET SILENCE_LENGTH 0.05\n")
    sphinx_subprocess.stdin.write("SET BEAM 1e-70\n")
    sphinx_subprocess.stdin.write("SET PBEAM 1e-70\n")
    sphinx_subprocess.stdin.write("SET WEND_BEAM 1e-70\n")
    sphinx_subprocess.stdin.write("SET WBEAM 1e-60\n")
    sphinx_subprocess.stdin.write("SET MAXHMMPF 2500\n")
    sphinx_subprocess.stdin.write("SET MAXCDSENPF 1500\n")
    sphinx_subprocess.stdin.write("SET MAXHISTPF 100\n")
    sphinx_subprocess.stdin.write("SET MAXWPF 20\n")
    sphinx_subprocess.stdin.write("SET SUBVQBEAM 1e-2\n")
    sphinx_subprocess.stdin.write("RESET BEAM\n")
    sphinx_subprocess.stdin.write("SET LM view\n")
    wx.PostEvent(parentFrame, ModeEvent("view"))


def handleSpeech(parentFrame):
    global lastCmd, repeatCmd, modifierList, status, mode, spacer, lastUttId, sphinx_subprocess, sphinx_cmd, HYP_PATH, VOICE_KEYBOARD_LOG_PATH, cmdWords, otherKeypressWords, asciiKeypressWords, numberWords, modifierWords,sphinx_config, DICTATION_HYP_PATH, KEYBOARD_HYP_PATH, waitingForVoiceCmd, stoppedStatus

    try:
        hyplines = open(HYP_PATH, 'r').readlines()
        if hyplines:
            hyp = hyplines[-1]
            #print '****'
            #print `hyp`
            #regexp = r'^(.*)\((\S+)\s+(\S+)\)' # -- for pocketsphinx
            regexp = r'^([^()]*)\((\d+)\)' # -- for sphinx3_livesegment
            #print regexp
            m = match(regexp, hyp.strip())
            if not m:
                return
            #print `m.groups(1)`
            utt = split(' ', m.groups(1)[0].upper())
            uttId = int(m.groups(1)[1])
            #uttScore = int(m.groups(1)[2])
            if uttId != lastUttId[HYP_PATH]:
                lastUttId[HYP_PATH] = uttId
                print `hyp`
                print `m.groups(1)`
                print `utt`

                utt = filter(lambda x : (x != ''), utt)
                if not len(utt):
                    return
                
                if not (status == "stopped"):

                    if filter(lambda x : (x == 'VOICE'), utt):
                        #print "Control word"
                        pause()
                        waitingForVoiceCmd=False
                        
                        for l in range(len(utt)):
                            if utt[l] == 'VOICE':
                                if len(utt)>l+1:
                                    if utt[l+1] == 'MISTAKE':
                                        resume()
                                        break

                                    if utt[l+1] == 'SPACES':
                                        spacer = ' '
                                        resume()
                                        break
                                    
                                    if utt[l+1] == 'UNDERSCORES':
                                        spacer = '_'
                                        resume()
                                        break

                                    if utt[l+1] == 'SQUASH':
                                        spacer = False
                                        resume()
                                        break

                                    if utt[l+1] == 'KEYBOARD':
                                        keyboardMode()
                                        resume()
                                        break

                                    if utt[l+1] == 'VIEW':
                                        viewMode()
                                        resume()
                                        break

                                    #if utt[l+1] == 'DICTATION':
                                    if utt[l+1] == 'REGULAR':
                                        regularMode()
                                        resume()
                                        break

                                    if utt[l+1] == 'RECOGNITION':
                                        resume()
                                        type_word('voice', spacer)
                                        type_word('recognition', spacer)
                                        lastCmd = ()
                                        modifierList = []

                                        break 

                                else:
                                    waitingForVoiceCmd=True 
                        pass
                    else:
                        for w in utt:
                            #print `w` + `repeatCmd`
                            if repeatCmd:
                                #print "Control word"
                                if numberWords.get(w):
                                    repeatNum = numberWords.get(w)
                                    for i in range(repeatNum-1):
                                        for cmd in repeatCmd:
                                            os.spawnvp(cmd[2], cmd[0], cmd[1])
                                repeatCmd = None
                                modifierList = []

                            elif modifierWords.get(w):
                                modifierList.extend(modifierWords.get(w))
                                print `modifierList`

                            elif asciiKeypressWords.get(w) or otherKeypressWords.get(w):
                                if asciiKeypressWords.get(w):
                                    #kPopen(cmdWords.get(w), shell=True)
                                    if VIRTUAL_KEYBOARD_PROGRAM == 'FAKEKEY_UINPUT':
                                        cmdArgs = []
                                        cmdArgs.append(FAKEKEY_UINPUT_PATH)
                                        cmdArgs.extend(modifierList)
                                        cmdArgs.extend(['-c', asciiKeypressWords.get(w)])
                                        cmd = (FAKEKEY_UINPUT_PATH, cmdArgs, os.P_WAIT)
                                    elif VIRTUAL_KEYBOARD_PROGRAM == 'XDOTOOL':
                                        cmdArgs = []
                                        cmdArgs.append(XDOTOOL_PATH)
                                        cmdArgs.append('key')
                                        cmdArgs.append(string.join(modifierList,'+') + '+' + asciiKeypressWords.get(w))
                                        cmd = (XDOTOOL_PATH, cmdArgs, os.P_WAIT)
                                elif otherKeypressWords.get(w):
                                    if VIRTUAL_KEYBOARD_PROGRAM == 'FAKEKEY_UINPUT':
                                        cmdArgs = []
                                        cmdArgs.append(FAKEKEY_UINPUT_PATH)
                                        cmdArgs.extend(modifierList)
                                        cmdArgs.extend(['-k', otherKeypressWords.get(w)])
                                        #print `cmdArgs`
                                        cmd = (FAKEKEY_UINPUT_PATH,cmdArgs, os.P_WAIT)
                                    elif VIRTUAL_KEYBOARD_PROGRAM == 'XDOTOOL':
                                        cmdArgs = []
                                        cmdArgs.append(XDOTOOL_PATH)
                                        cmdArgs.append('key')
                                        cmdArgs.append(string.join(modifierList,'+') + '+' + otherKeypressWords.get(w))
                                        cmd = (XDOTOOL_PATH, cmdArgs, os.P_WAIT)
                                print `cmd`
                                os.spawnvp(cmd[2],cmd[0],cmd[1])
                                lastCmd = [cmd]
                                modifierList = []

                            elif cmdWords.get(w):
                                #kPopen(cmdWords.get(w), shell=True)
                                cmds = cmdWords.get(w)
                                print `cmds`
                                for cmd in cmds:
                                    print `cmd`
                                    os.spawnvp(cmd[2],cmd[0],cmd[1])
                                lastCmd = cmds
                                modifierList = []



                            elif w == 'REPEAT_COMMAND':
                                #print "Control word"
                                repeatCmd = lastCmd

                            else:
                                if mode == 'words':
                                    type_word(w.lower(), spacer)
                                    lastCmd = ()
                                    modifierList = []
                                elif w.upper() in keystrokes_and_cmdWords_that_dont_type:
                                #if not mode:
                                    type_word(w.lower(), spacer)
                                    lastCmd = ()
                                    modifierList = []

                else:
                    if waitingForVoiceCmd:
                        waitingForVoiceCmd = False
                        w = utt[0]

                        if not (w == 'VOICE'):
                            utt = utt[1:]
                        
                        if w == 'MISTAKE':
                            resume()

                        if w == 'RECOGNITION':
                            resume()
                            type_word('voice', spacer)
                            type_word('recognition', spacer)
                            lastCmd = ()
                            modifierList = []


                        if w == 'SPACES':
                            spacer = ' '
                            resume()
                            return

                        if w == 'UNDERSCORES':
                            spacer = '_'
                            resume()
                            return

                        if w == 'SQUASH':
                            spacer = False
                            resume()
                            return



                    if (status == "stopped"):
                        for w in utt:
                            print `status`
                            print `w`
                            if w == 'VOICE':
                                stoppedStatus = 1;
                            elif stoppedStatus == 1:
                                if w == 'CONTROL':
                                    resume()
                                else:
                                    stoppedStatus = 0;
                            #else:
                            #    status = "stopped"
                            #    stoppedStatus = 0;
                sleep(0.1)
            else:
                sleep(0.1)
    except (KeyboardInterrupt, SystemExit):
        raise
    except IOError:
        pass
 #   except:
 #       pass



#text, segs = _pocketsphinx.get_hypothesis()
#print `text`
#print `text.strip()`


#_pocketsphinx.close()

EVT_STATUS_ID = wx.NewId()

def EVT_STATUS(win, func):
    win.Connect(-1, -1, EVT_STATUS_ID, func)

class StatusEvent(wx.PyEvent):
    def __init__(self, data):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_STATUS_ID)
        self.data = data


EVT_MODE_ID = wx.NewId()

def EVT_MODE(win, func):
    win.Connect(-1, -1, EVT_MODE_ID, func)

class ModeEvent(wx.PyEvent):
    def __init__(self, data):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_MODE_ID)
        self.data = data



class WorkerThread(Thread):

    def __init__(self, parentFrame):
        Thread.__init__(self)
        self.parentFrame = parentFrame
        self.start()



    def run(self):
        while True:
            handleSpeech(self.parentFrame)
            #if self._want_abort:
                # Use a result of None to acknowledge the abort (of
                # course you can use whatever you'd like or even
                # a separate event type)
                #wxPostEvent(self._notify_window,ResultEvent(None))
                #return
        # Here's where the result would be returned (this is an
        # example fixed result of the number 10, but it could be
        # any Python object)
        #wxPostEvent(self.parent,ResultEvent(10))



def getIconBitmap(status, mode, spacer):
#        if mode:
#            color = [255,0,0]
#        else:
#            color = [0,255,0]

    status_to_color = {
        "busy" : [0,0,255],
        "ready" : [0,255,0],
        "stopped" : [255,0,0],
        }

    mode_to_shape = {
        "words" : "x"*(16**2),
        "keyboard" : "o"*(16**2/2) + "x"*(16**2/2),
        "view" : "x"*(16**2/2) + "o"*(16**2/2),
        }

    
    color = status_to_color[status]
    shape = mode_to_shape[mode]
    print ("****************" + `color`)
    print ("****************" + `shape`)
    
    image = wx.EmptyImage(16,16)
    #s = string.join(map(chr,color),'')*(16**2)
    foreground = string.join(map(chr,color),'')
    background = string.join(map(chr,[0,0,0]),'')
    s = string.replace(shape, "o", background)
    s = string.replace(s, "x", foreground)
    image.SetData(s)
                
    bmp = image.ConvertToBitmap()
    bmp.SetMask(wx.Mask(bmp, wx.WHITE)) #sets the transparency colour to white 
        
    icon = wx.EmptyIcon()
    icon.CopyFromBitmap(bmp)
    return icon

class MyTaskBarIcon(wx.TaskBarIcon):
    def __init__(self, frame):
        global mode, status

        wx.TaskBarIcon.__init__(self)
        self.frame = frame
        #icon = getIconBitmap("ready", "dictation", " ")
        icon = getIconBitmap(status, mode, " ")
        #icon = getIconBitmap("stopped", "words", " ")

        print "About to call RemoveIcon; IsIconInstalled = " + repr(self.IsIconInstalled())
        self.RemoveIcon()
        print "Called RemoveIcon; IsIconInstalled = " + repr(self.IsIconInstalled())
        self.SetIcon(icon, "test")
        print "Called SetIcon; IsIconInstalled = " + repr(self.IsIconInstalled())

class TaskBarFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, -1, title, size = (1, 1),
            style=wx.FRAME_NO_TASKBAR|wx.NO_FULL_REPAINT_ON_RESIZE)
        self.tbicon = MyTaskBarIcon(self)
        self.Show(True)

class MyApp(wx.App):
    def OnInit(self):
        self.frame = TaskBarFrame(None, -1, ' ')
        self.frame.Center(wx.BOTH)
        self.frame.Show(False)
        #print "debug 55"
        #sleep(50)
        EVT_MODE(self,self.OnMode)
        EVT_STATUS(self,self.OnStatus)

        global parentFrame
        parentFrame = self
        
        self.worker = WorkerThread(self)
        return True

    
    def OnMode(self, ev):
        print "OnMode invoked"
        print "About to call RemoveIcon; IsIconInstalled = " + repr(self.frame.tbicon.IsIconInstalled())
        self.frame.tbicon.RemoveIcon()
        print "Called RemoveIcon; IsIconInstalled = " + repr(self.frame.tbicon.IsIconInstalled())
        self.frame.tbicon = MyTaskBarIcon(self)
    def OnStatus(self, ev):
        print "OnStatus invoked"
        print "About to call RemoveIcon; IsIconInstalled = " + repr(self.frame.tbicon.IsIconInstalled())
        self.frame.tbicon.RemoveIcon()
        print "Called RemoveIcon; IsIconInstalled = " + repr(self.frame.tbicon.IsIconInstalled())
        self.frame.tbicon = MyTaskBarIcon(self)

def main(argv=None):
    if argv is None:
        argv = sys.argv

    app = MyApp(0)
    regularMode()
#    keyboardMode()
    sleep(6)
    resume()
    app.MainLoop()

if __name__ == '__main__':
    main()

