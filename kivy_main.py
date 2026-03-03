# -*- coding: utf-8 -*-
import math
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, ListProperty, NumericProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.factory import Factory
from kivy.core.window import Window
from kivy.metrics import dp

# Set window size for testing on desktop to simulate mobile
Window.size = (400, 700)

# Register CJK Font for Windows/Android
from kivy.core.text import LabelBase
import os

def register_fonts():
    # Search order: 1) bundled font in app dir, 2) Windows system, 3) Android system
    app_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(app_dir, "msjh.ttc"),          # Bundled (Windows font, copied to app dir)
        os.path.join(app_dir, "NotoSansCJK.otf"),   # Bundled Noto (open source alternative)
        "C:\\Windows\\Fonts\\msjh.ttc",              # Windows system font
        "/system/fonts/NotoSansCJK-Regular.ttc",     # Android system font
        "/system/fonts/DroidSansFallback.ttf",       # Older Android fallback
    ]
    for font_path in candidates:
        if os.path.exists(font_path):
            LabelBase.register(name="DroidSansFallback", fn_regular=font_path)
            print(f"[Font] Registered CJK font: {font_path}")
            return
    print("[Font] WARNING: No CJK font found. Chinese characters may not display correctly.")

register_fonts()

class MedicalData:
    DRUG_STABILITY = [
        {"name": "Alprostadil (Prostin VR) 500mcg/mL/Amp", "storage": "冷藏 2-8°C", "stability": "開瓶即棄；室溫: 24 hrs", "prep": "1 Amp + NS 25-250mL (如加至250mL, 濃度為 2 mcg/mL)", "bolus": "--", "rate": "0.01-0.4 mcg/kg/min", "calc": {"unit": "mcg/kg/min", "amt": 0.5, "vol": 250, "factor": 60, "type": "mcg"}},
        {"name": "Dobutamine (Gendobu) 250mg/20mL/Vial", "storage": "室溫", "stability": "室溫: 24 hrs", "prep": "2 Vial (500mg) + NS/D5W 500mL (1mg/mL)", "bolus": "--", "rate": "2-20 μg/kg/min (max 40)", "calc": {"unit": "mcg/kg/min", "amt": 500, "vol": 500, "factor": 60, "type": "mcg"}},
        {"name": "Dopamine (Dopamin) 200mg/5mL/Amp", "storage": "室溫 避光", "stability": "開瓶即棄；室溫: 24 hrs", "prep": "4 Amp (800mg) + NS 500mL (1.6mg/mL)", "bolus": "--", "rate": "2-20 μg/kg/min", "calc": {"unit": "mcg/kg/min", "amt": 800, "vol": 500, "factor": 60, "type": "mcg"}},
        {"name": "Epinephrine (Adrenalin) 1mg/mL/Amp", "storage": "室溫 避光", "stability": "開瓶即棄 (丟棄)", "prep": "5 Amp (5mg) + NS 500mL (10μg/mL)", "bolus": "--", "rate": "0.01-0.1 mcg/kg/min", "calc": {"unit": "mcg/kg/min", "amt": 5, "vol": 500, "factor": 60, "type": "mcg"}},
        {"name": "Heparin (Agglutex) 25000U/5mL", "storage": "室溫 避光", "stability": "開封冷藏1個月", "prep": "20000 U + NS 500mL (40U/mL)", "bolus": "1mL/kg (Max 125mL)", "rate": "12-20 U/kg/h", "calc": {"unit": "U/kg/hr", "amt": 20000, "vol": 500, "factor": 1, "type": "U"}},
        {"name": "Norepinephrine 4mg/4mL", "storage": "室溫 避光", "stability": "室溫 24 hrs", "prep": "2 Vial (8mg) + D5W 500mL (16μg/mL)", "bolus": "--", "rate": "0.01-0.1 mcg/kg/min", "calc": {"unit": "mcg/kg/min", "amt": 8, "vol": 500, "factor": 60, "type": "mcg"}},
        {"name": "NTG (Glyceryl trinitrate) 50mg/10mL", "storage": "室溫 避光", "stability": "開瓶即棄；室溫 24 hrs", "prep": "1 Amp (50mg) + D5W 490mL (100μg/mL) = 500mL", "bolus": "--", "rate": "5-100 mcg/min", "calc": {"unit": "mcg/min (不計體重)", "amt": 50, "vol": 500, "factor": 60, "type": "mcg_fixed"}},
        {"name": "Atracurium (Genso) 25mg/2.5mL/Amp", "storage": "冷藏避光", "stability": "開瓶即棄", "prep": "8 Amp (200mg) +NS 80mL (2mg/mL)", "bolus": "0.4-0.5 mg/kg", "rate": "0.3-0.6 mg/kg/hr", "calc": {"unit": "mg/kg/hr", "amt": 200, "vol": 100, "factor": 1, "type": "mg"}},
        {"name": "Dexmedetomidine (Precedex) 200mcg/2mL", "storage": "室溫", "stability": "開瓶即棄", "prep": "1 vial (200mcg=0.2mg) + 48 mL N/S", "bolus": "0.5-1 μg/kg", "rate": "0.2-1 μg/kg/h", "calc": {"unit": "mcg/kg/hr", "amt": 0.2, "vol": 50, "factor": 1, "type": "mcg"}},
        {"name": "Esmolol 100mg/10mL/Vial", "storage": "室溫", "stability": "7 days", "prep": "Undiluted (10mg/mL)", "bolus": "0.05mL/kg", "rate": "0.05-0.3 mg/kg/min", "calc": {"unit": "mg/kg/min", "amt": 100, "vol": 10, "factor": 60, "type": "mg"}},
        {"name": "Fentanyl 0.5mg/10mL/Amp", "storage": "室溫避光", "stability": "24 hrs", "prep": "1 Amp (0.5mg) + NS 40 mL (10μg/mL)", "bolus": "1mL/5mL", "rate": "0.5-2 μg/kg/hr", "calc": {"unit": "mcg/kg/hr", "amt": 0.5, "vol": 50, "factor": 1, "type": "mcg"}},
        {"name": "Isoproterenol (Proternol-L) 0.2mg/mL", "storage": "室溫 避光", "stability": "24 hrs", "prep": "10Amp (2mg) + D5W 500mL (4μg/mL)", "bolus": "--", "rate": "0.01-0.1 mcg/kg/min", "calc": {"unit": "mcg/kg/min", "amt": 2, "vol": 500, "factor": 60, "type": "mcg"}},
        {"name": "Milrinone (Primacor) 10mg/10mL", "storage": "室溫", "stability": "3天", "prep": "1Amp (10mg) + NS 40mL (0.2mg/mL)", "bolus": "50μg/kg", "rate": "0.375-0.75μg/kg/min", "calc": {"unit": "mcg/kg/min", "amt": 10, "vol": 50, "factor": 60, "type": "mcg"}},
        {"name": "Nicardipine (Nicarpine) 10mg/10mL", "storage": "室溫 避光", "stability": "24 hrs", "prep": "2Amp (20mg) + NS 20mL (0.5mg/mL)", "bolus": "--", "rate": "0.5-5 mcg/kg/min", "calc": {"unit": "mcg/kg/min", "amt": 20, "vol": 40, "factor": 60, "type": "mcg"}},
        {"name": "Propofol (Fresofol/Lipuro) 200mg/20mL", "storage": "室溫", "stability": "6h", "prep": "Undiluted (10mg/mL)", "bolus": "0.25-1mg/kg", "rate": "0.3-3mg/kg/hr", "calc": {"unit": "mg/kg/hr", "amt": 200, "vol": 20, "factor": 1, "type": "mg"}},
        {"name": "Vasopressin (Pitressin) 20U/mL", "storage": "室溫", "stability": "Unknown", "prep": "Shock: 1Amp (20U) + D5W 25mL", "bolus": "VT/VF: 2 Amp", "rate": "0.01-0.04 U/min", "calc": {"unit": "U/min (不計體重)", "amt": 20, "vol": 25, "factor": 60, "type": "U_fixed"}},
    ]

    ABX_GUIDE = [
        {"name": "Acyclovir (IV)", "no_adj": False, "rules": [
            {"min": 50, "dose": "5-10 mg/kg q8h"},
            {"min": 25, "max": 49, "dose": "5-10 mg/kg q12h"},
            {"min": 10, "max": 24, "dose": "5-10 mg/kg q24h"},
            {"max": 9, "dose": "2.5-5 mg/kg q24h"}
        ], "notes": "肥胖調整: BMI >= 30 時，建議使用 AdjBW 或 IBW。"},
        {"name": "Amikacin (IV)", "no_adj": False, "rules": [
            {"min": 60, "dose": "15 mg/kg q24h"},
            {"min": 40, "max": 59, "dose": "15 mg/kg q36h"},
            {"min": 20, "max": 39, "dose": "15 mg/kg q48h"},
            {"max": 19, "dose": "建議諮詢藥師 (TDM)。"}
        ], "notes": "建議使用 TDM 監測。"},
        {"name": "Amoxicillin/Clavulanate (Augmentin) (IV)", "no_adj": False, "rules": [
            {"min": 31, "dose": "1.2 g q8h (Standard)"},
            {"min": 10, "max": 30, "dose": "首劑 1.2 g，隨後 600 mg q12h"},
            {"max": 10, "dose": "首劑 1.2 g，隨後 600 mg q24h"}
        ], "notes": "血液透析 (HD): 透析期間與結束時各額外補給 600 mg。"},
        {"name": "Ampicillin (IV)", "no_adj": False, "rules": [
            {"min": 50, "dose": "1-2 g q4-6h"},
            {"min": 10, "max": 49, "dose": "1-2 g q6-12h"},
            {"max": 10, "dose": "1-2 g q12-24h"}
        ]},
        {"name": "Ampicillin/Sulbactam (Unasyn) (IV)", "no_adj": False, "rules": [
            {"min": 30, "dose": "1.5-3 g q6h"},
            {"min": 15, "max": 29, "dose": "1.5-3 g q12h"},
            {"max": 14, "dose": "1.5-3 g q24h"}
        ]},
        {"name": "Cefazolin (IV)", "no_adj": False, "rules": [
            {"min": 35, "dose": "1-2 g q8h"},
            {"min": 11, "max": 34, "dose": "1-2 g q12h"},
            {"max": 10, "dose": "1-2 g q24h"}
        ]},
        {"name": "Cefepime (IV)", "no_adj": False, "rules": [
            {"min": 60, "dose": "1-2 g q8-12h"},
            {"min": 30, "max": 50, "dose": "1-2 g q12h"},
            {"min": 11, "max": 29, "dose": "1 g q24h"},
            {"max": 10, "dose": "0.5-1 g q24h"}
        ]},
        {"name": "Ceftriaxone (IV)", "no_adj": True, "rules": [
            {"min": 0, "dose": "1-2 g q24h (Standard)。不必隨腎功調整。"}
        ]},
        {"name": "Meropenem (IV)", "no_adj": False, "rules": [
            {"min": 51, "dose": "1 g q8h"},
            {"min": 26, "max": 50, "dose": "1 g q12h"},
            {"min": 10, "max": 25, "dose": "500 mg q12h"},
            {"max": 9, "dose": "500 mg q24h"}
        ]},
        {"name": "Vancomycin (IV)", "no_adj": False, "rules": [
            {"min": 0, "dose": "請參考 Vancomycin 專屬劑量規範與血品濃度偵測 (TDM)。"}
        ]}
    ]
    
    PD_ABX_CONT = ["Vancomycin", "Cefazolin", "Ceftazidime", "Cefepime", "Meropenem", "Ampicillin", "Teicoplanin"]
    PD_ABX_INT = ["Vancomycin", "Cefazolin", "Ceftazidime", "Gentamicin", "Amikacin", "Meropenem", "Teicoplanin"]

# KV Design
KV = '''
#:import ButtonBehavior kivy.uix.behaviors.ButtonBehavior
#:import hex kivy.utils.get_color_from_hex
#:import Factory kivy.factory.Factory
#:import Window kivy.core.window.Window
#:import Spinner kivy.uix.spinner.Spinner

<Label>:
    font_name: 'DroidSansFallback'

<Button>:
    font_name: 'DroidSansFallback'

<TextInput>:
    font_name: 'DroidSansFallback'

<SelectionRow@ButtonBehavior+BoxLayout>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(45)
    canvas.before:
        Color:
            rgba: (0.9, 0.9, 0.9, 1) if self.state == 'down' else (1, 1, 1, 1)
        Rectangle:
            pos: self.pos
            size: self.size
            
<NavButton@Button>:
    background_normal: ''
    background_color: hex('#2196F3')
    color: 1, 1, 1, 1
    font_size: '16sp'
    size_hint_y: None
    height: dp(55)
    canvas.before:
        Color:
            rgba: (1, 1, 1, 0.1) if self.state == 'normal' else (1, 1, 1, 0.3)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12)]

<HeaderLabel@Label>:
    font_size: '22sp'
    bold: True
    size_hint_y: None
    height: dp(60)
    color: hex('#0D47A1')

<CalcButton@Button>:
    background_normal: ''
    background_color: hex('#4CAF50')
    color: 1, 1, 1, 1
    bold: True
    size_hint_y: None
    height: dp(55)

<ResultBox@Label>:
    size_hint_y: None
    height: self.texture_size[1] + dp(20)
    text_size: self.width - dp(20), None
    halign: 'left'
    valign: 'top'
    color: 0, 0, 0, 1
    font_name: 'DroidSansFallback' if Window.softinput_mode == '' else 'Roboto' 
    canvas.before:
        Color:
            rgba: hex('#FFFFFF')
        Rectangle:
            pos: self.pos
            size: self.size

<CalcInput@BoxLayout>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(45)
    label_text: ''
    input_text: ''
    Label:
        text: root.label_text
        color: 0, 0, 0, 1
        size_hint_x: 0.4
    TextInput:
        id: ti
        text: root.input_text
        multiline: False
        size_hint_x: 0.6
        input_filter: 'float'

<ChoiceRow@BoxLayout>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(45)
    label_text: ''
    Label:
        text: root.label_text
        color: 0, 0, 0, 1
        size_hint_x: 0.4

<TitrationPopup@Popup>:
    title: '藥物詳情 / 流速計算'
    title_font: 'DroidSansFallback'
    size_hint: 0.95, 0.95
    BoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(8)
        canvas.before:
            Color:
                rgba: 0.15, 0.15, 0.15, 1
            Rectangle:
                pos: self.pos
                size: self.size
        ScrollView:
            size_hint_y: 0.45
            Label:
                id: info_text
                text: ''
                size_hint_y: None
                height: self.texture_size[1]
                text_size: self.width, None
                color: 1, 1, 1, 1
        GridLayout:
            id: inputs_grid
            cols: 2
            size_hint_y: None
            height: self.minimum_height
            spacing: dp(5)
            row_default_height: dp(40)
        Label:
            id: result_label
            text: ''
            size_hint_y: None
            height: dp(50)
            color: 0.3, 1, 0.5, 1
            bold: True
            font_size: dp(16)
        Button:
            text: '關閉'
            size_hint_y: None
            height: dp(45)
            on_release: root.dismiss()


ScreenManager:
    MainMenu:
    RSIScreen:
    ABXScreen:
    PDScreen:
    VancoScreen:
    AminoScreen:
    PJPScreen:
    HypoNaScreen:
    DrugScreen:

<MainMenu>:
    name: 'main'
    canvas.before:
        Color:
            rgba: hex('#F0F2f5')
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(15)
        
        HeaderLabel:
            text: '阿山哥醫學計算機'
            font_size: '26sp'
        
        Label:
            text: '專業臨床決策輔助工具'
            color: hex('#666666')
            size_hint_y: None
            height: dp(30)
            
        ScrollView:
            GridLayout:
                cols: 1
                spacing: dp(12)
                size_hint_y: None
                height: self.minimum_height
                
                NavButton:
                    text: 'RSI 快速誘導插管'
                    on_release: root.manager.current = 'rsi'
                NavButton:
                    text: 'ABX 腎功能抗生素'
                    on_release: root.manager.current = 'abx'
                NavButton:
                    text: 'PD 腹膜透析腹膜炎'
                    on_release: root.manager.current = 'pd'
                NavButton:
                    text: 'Vancomycin TDM'
                    on_release: root.manager.current = 'vanco'
                NavButton:
                    text: 'Amino HDEI'
                    on_release: root.manager.current = 'amino'
                NavButton:
                    text: 'PJP 治療指引'
                    on_release: root.manager.current = 'pjp'
                NavButton:
                    text: '低血鈉校正'
                    on_release: root.manager.current = 'hypona'
                NavButton:
                    text: '藥物安定性'
                    on_release: root.manager.current = 'drugs'

<PJPScreen>:
    name: 'pjp'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(15)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: hex('#FFFFFF')
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            Button:
                text: '返回'
                size_hint_x: None
                width: dp(80)
                on_release: root.manager.current = 'main'
            HeaderLabel:
                text: 'PJP 治療'
        
        GridLayout:
            cols: 2
            size_hint_y: None
            height: dp(140)
            Label:
                text: '性別:'
                color:0,0,0,1
            BoxLayout:
                CheckBox:
                    group: 'pjp_gender'
                    active: True
                    id: pjp_male
                Label:
                    text: '男'
                    color: 0,0,0,1
                CheckBox:
                    group: 'pjp_gender'
                    id: pjp_female
                Label:
                    text: '女'
                    color: 0,0,0,1
            Label:
                text: '年齡 (yrs):'
                color:0,0,0,1
            TextInput:
                id: age
                text: '60'
                input_filter: 'int'
            Label:
                text: '體重 (kg):'
                color:0,0,0,1
            TextInput:
                id: w
                text: '70'
                input_filter: 'float'
            Label:
                text: 'SCr (mg/dL):'
                color:0,0,0,1
            TextInput:
                id: scr
                text: '1.0'
                input_filter: 'float'
        
        ChoiceRow:
            label_text: '透析狀態:'
            Spinner:
                id: pjp_dialysis
                text: '無透析 (None)'
                values: ['無透析 (None)', '血液透析 (HD)']
                size_hint_x: 0.6
        
        CalcButton:
            text: '開始計算建議劑量'
            on_release: root.calculate()
            
        ScrollView:
            ResultBox:
                id: res
                text: '結果顯示...'

<HypoNaScreen>:
    name: 'hypona'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(15)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: hex('#FFFFFF')
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            Button:
                text: '返回'
                size_hint_x: None
                width: dp(80)
                on_release: root.manager.current = 'main'
            HeaderLabel:
                text: '低血鈉校正'
        
        GridLayout:
            cols: 2
            size_hint_y: None
            height: dp(140)
            Label:
                text: '性別:'
                color:0,0,0,1
            BoxLayout:
                CheckBox:
                    group: 'na_gender'
                    active: True
                    id: na_male
                Label:
                    text: '男'
                    color: 0,0,0,1
                CheckBox:
                    group: 'na_gender'
                    id: na_female
                Label:
                    text: '女'
                    color: 0,0,0,1
            Label:
                text: '年齡 (yrs):'
                color:0,0,0,1
            TextInput:
                id: age
                text: '60'
                input_filter: 'int'
            Label:
                text: '體重 (kg):'
                color:0,0,0,1
            TextInput:
                id: w
                text: '70'
                input_filter: 'float'
            Label:
                text: '現況 Na+ (mEq/L):'
                color:0,0,0,1
            TextInput:
                id: na
                text: '120'
                input_filter: 'float'
        
        ChoiceRow:
            label_text: '補給液種類:'
            Spinner:
                id: fluid_spinner
                text: '3% NaCl (513 mEq/L)'
                values: ['3% NaCl (513 mEq/L)', '0.9% NaCl (154 mEq/L)', '0.45% NaCl (77 mEq/L)', 'D5W (0 mEq/L)']
                size_hint_x: 0.6

        CalcButton:
            text: '計算校正速率'
            on_release: root.calculate()
            
        ScrollView:
            ResultBox:
                id: res
                text: '結果顯示...'

<DrugScreen>:
    name: 'drugs'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(15)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: hex('#FFFFFF')
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            Button:
                text: '返回'
                size_hint_x: None
                width: dp(80)
                on_release: root.manager.current = 'main'
            HeaderLabel:
                text: '藥物安定性'
        
        TextInput:
            id: search
            hint_text: '搜尋藥物...'
            size_hint_y: None
            height: dp(40)
            multiline: False
            on_text: root.filter_drugs(self.text)
            
        ScrollView:
            GridLayout:
                id: drug_list
                cols: 1
                spacing: dp(5)
                size_hint_y: None
                height: self.minimum_height

<RSIScreen>:
    name: 'rsi'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(15)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: hex('#FFFFFF')
            Rectangle:
                pos: self.pos
                size: self.size
                
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            Button:
                text: '返回'
                size_hint_x: None
                width: dp(80)
                on_release: root.manager.current = 'main'
            HeaderLabel:
                text: 'RSI 劑量'
        
        CalcInput:
            label_text: '體重 (kg):'
            input_text: '70'
            id: weight_input
            
        ChoiceRow:
            label_text: '臨床情境:'
            Spinner:
                id: scenario_spinner
                text: '一般情境 (Routine)'
                values: ['一般情境 (Routine)', '休克/低血壓 (Shock/Hypotension)', '氣喘/支氣管痙攣 (Asthma/Bronchospasm)', '頭部外傷/增加 ICP (Head Injury/ICP)']
                size_hint_x: 0.6
        
        Label:
            text: '1. 選擇誘導藥物 (Induction):'
            color: 0,0,0,1
            size_hint_y: None
            height: dp(30)
        ScrollView:
            size_hint_y: 0.2
            GridLayout:
                id: drug_choices_ind
                cols: 1
                size_hint_y: None
                height: self.minimum_height
        
        Label:
            text: '2. 選擇肌鬆劑 (Paralytics):'
            color: 0,0,0,1
            size_hint_y: None
            height: dp(30)
        ScrollView:
            size_hint_y: 0.15
            GridLayout:
                id: drug_choices_para
                cols: 1
                size_hint_y: None
                height: self.minimum_height

        CalcButton:
            text: '計算 RSI 建議劑量'
            on_release: root.calculate()
            
        ScrollView:
            ResultBox:
                id: result_label
                text: '在此顯示結果...'

<ABXScreen>:
    name: 'abx'
    curr_egfr: -1
    BoxLayout:
        orientation: 'vertical'
        padding: dp(15)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: hex('#FFFFFF')
            Rectangle:
                pos: self.pos
                size: self.size
                
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            Button:
                text: '返回'
                size_hint_x: None
                width: dp(80)
                on_release: root.manager.current = 'main'
            HeaderLabel:
                text: 'ABX 劑量調整'
        
        GridLayout:
            cols: 2
            spacing: dp(5)
            size_hint_y: None
            height: dp(130)
            Label:
                text: '年齡:'
                color: 0,0,0,1
            TextInput:
                id: age
                text: '60'
                input_filter: 'int'
            Label:
                text: '體重 (kg):'
                color: 0,0,0,1
            TextInput:
                id: weight
                text: '70'
                input_filter: 'float'
            Label:
                text: 'SCr (mg/dL):'
                color: 0,0,0,1
            TextInput:
                id: scr
                text: '1.0'
                input_filter: 'float'
        
        ChoiceRow:
            label_text: '性別:'
            BoxLayout:
                CheckBox:
                    group: ' gender'
                    active: True
                    id: gender_m
                Label:
                    text: '男'
                    color: 0,0,0,1
                CheckBox:
                    group: ' gender'
                    id: gender_f
                Label:
                    text: '女'
                    color: 0,0,0,1
        
        CalcButton:
            text: '計算 eGFR 並顯示藥物'
            on_release: root.calculate_egfr()
            
        Label:
            id: egfr_res
            text: 'eGFR: --'
            color: hex('#2196F3')
            bold: True
            size_hint_y: None
            height: dp(30)

        ScrollView:
            GridLayout:
                id: drug_list
                cols: 1
                spacing: dp(10)
                size_hint_y: None
                height: self.minimum_height

<PDScreen>:
    name: 'pd'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(15)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: hex('#FFFFFF')
            Rectangle:
                pos: self.pos
                size: self.size
                
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            Button:
                text: '返回'
                size_hint_x: None
                width: dp(80)
                on_release: root.manager.current = 'main'
            HeaderLabel:
                text: 'PD 劑量建議'
        
        CalcInput:
            label_text: '體重 (kg):'
            input_text: '60'
            id: pd_weight
        
        CalcInput:
            label_text: '單包體積 (L):'
            input_text: '2.0'
            id: pd_vol
            
        ChoiceRow:
            label_text: '透析方式:'
            Spinner:
                id: pd_mode
                text: '連續型 (Continuous)'
                values: ['連續型 (Continuous)', '間歇型 (Intermittent)']
                size_hint_x: 0.6
                
        Label:
            text: '選擇藥物 (可複選):'
            color: 0,0,0,1
            size_hint_y: None
            height: dp(30)
            
        ScrollView:
            size_hint_y: 0.3
            GridLayout:
                id: drug_choices
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                # Programmatically added checkboxes...

        CalcButton:
            text: '計算 PD 劑量'
            on_release: root.calculate()
            
        ScrollView:
            ResultBox:
                id: pd_res
                text: '結果將顯示於此...'

<VancoScreen>:
    name: 'vanco'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(15)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: hex('#FFFFFF')
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            Button:
                text: '返回'
                size_hint_x: None
                width: dp(80)
                on_release: root.manager.current = 'main'
            HeaderLabel:
                text: 'Vancomycin TDM'
        
        GridLayout:
            cols: 2
            size_hint_y: None
            height: dp(200)
            Label:
                text: '體重(kg):'
                color:0,0,0,1
            TextInput:
                id: w
                text: '70'
            Label:
                text: '身高(cm):'
                color:0,0,0,1
            TextInput:
                id: h
                text: '170'
            Label:
                text: '年齡:'
                color:0,0,0,1
            TextInput:
                id: a
                text: '60'
            Label:
                text: 'SCr:'
                color:0,0,0,1
            TextInput:
                id: s
                text: '1.0'
            Label:
                text: '性別:'
                color:0,0,0,1
            BoxLayout:
                CheckBox:
                    group: 'v_gender'
                    active: True
                    id: v_male
                Label:
                    text: '男'
                    color: 0,0,0,1
                CheckBox:
                    group: 'v_gender'
                    id: v_female
                Label:
                    text: '女'
                    color: 0,0,0,1

        CalcButton:
            text: '計算 Vanco 劑量'
            on_release: root.calculate()

        ScrollView:
            ResultBox:
                id: res
                text: '等待計算...'

<AminoScreen>:
    name: 'amino'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(15)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: hex('#FFFFFF')
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            Button:
                text: '返回'
                size_hint_x: None
                width: dp(80)
                on_release: root.manager.current = 'main'
            HeaderLabel:
                text: 'Amino HDEI'
        
        CalcInput:
            label_text: '體重 (kg):'
            input_text: '70'
            id: w
        CalcInput:
            label_text: '身高 (cm):'
            input_text: '170'
            id: h
        ChoiceRow:
            label_text: '藥物名稱:'
            Spinner:
                id: am_drug
                text: 'Amikacin'
                values: ['Amikacin', 'Gentamicin']
                size_hint_x: 0.6
        ChoiceRow:
            label_text: '性別:'
            BoxLayout:
                CheckBox:
                    group: 'am_gender'
                    active: True
                    id: am_male
                Label:
                    text: '男'
                    color: 0,0,0,1
                CheckBox:
                    group: 'am_gender'
                    id: am_female
                Label:
                    text: '女'
                    color: 0,0,0,1

        CalcButton:
            text: '計算 Amino 劑量'
            on_release: root.calculate()
            
        ScrollView:
            ResultBox:
                id: res
                text: '等待計算...'

'''

class MainMenu(Screen):
    pass

class RSIScreen(Screen):
    def on_enter(self):
        self.ids.drug_choices_ind.clear_widgets()
        self.ids.drug_choices_para.clear_widgets()
        
        ind_drugs = ["Etomidate", "Ketamine", "Propofol", "Midazolam", "Thiopental"]
        para_drugs = ["Succinylcholine", "Rocuronium"]
        
        # Helper to create clickable rows
        def create_drug_row(drug_name):
            row = Factory.SelectionRow()
            cb = CheckBox(size_hint_x=None, width=dp(50), color=(0.2, 0.6, 1, 1))
            lbl = Label(text=drug_name, color=(0,0,0,1), halign='left', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            row.add_widget(cb)
            row.add_widget(lbl)
            
            # Store references
            row.cb = cb
            row.lbl = lbl
            
            # Toggle checkbox on button release
            row.bind(on_release=lambda x: setattr(cb, 'active', not cb.active))
            return row

        for drug in ind_drugs:
            self.ids.drug_choices_ind.add_widget(create_drug_row(drug))
            
        for drug in para_drugs:
            self.ids.drug_choices_para.add_widget(create_drug_row(drug))

    def calculate(self):
        try:
            wt = float(self.ids.weight_input.ids.ti.text)
            setting = self.ids.scenario_spinner.text
            
            res = f"【RSI 建議劑量 - {setting}】\n計算基準: 體重 {wt} kg\n"
            res += "-" * 30 + "\n"
            
            # Induction Logic
            res += "[誘導藥物 (Induction)]\n"
            selected_ind = []
            # children are in reverse order of addition
            for child in self.ids.drug_choices_ind.children[::-1]:
                if hasattr(child, 'cb') and child.cb.active:
                    selected_ind.append(child.lbl.text)
            
            ind_data = {
                "Etomidate": {"dose": 0.3, "notes": "Onset 15-45s, 循環穩定。"},
                "Ketamine": {"dose": 2.0, "notes": "Onset 30-60s, 支氣管擴張，維持血壓。"},
                "Propofol": {"dose": 1.5, "notes": "Onset 15-45s, 強效支氣管擴張，但會降血壓。"},
                "Midazolam": {"dose": 0.2, "notes": "Onset 30-60s, 作為誘導劑效果不一。"},
                "Thiopental": {"dose": 3.0, "notes": "Onset 30s, 降腦壓但降血壓。"}
            }
            
            for drug in selected_ind:
                d = ind_data[drug]
                calc_dose = d['dose'] * wt
                advice = ""
                if "Shock" in setting:
                    if drug == "Ketamine": advice = "⭐ 首選。虛弱者劑量可減半。"
                    elif drug == "Propofol": 
                        advice = "⚠️ 慎用！建議減量至 0.5-1.0 mg/kg。"
                        calc_dose = 0.75 * wt
                    elif drug == "Etomidate": advice = "⭐ 常用藥物指標。"
                elif "Asthma" in setting and drug in ["Ketamine", "Propofol"]:
                    advice = "⭐ 首選藥物 (支氣管擴張)。"
                elif "Head" in setting:
                    if drug == "Etomidate": advice = "⭐ 常用。維持灌流壓。"
                    elif drug == "Thiopental": advice = "✅ 可降腦壓。"
                
                res += f"● {drug}: {calc_dose:.1f} mg\n"
                res += f"  特性: {d['notes']}\n"
                if advice: res += f"  建議: {advice}\n"
                res += "\n"
                
            # Paralytics Logic
            res += "[肌鬆劑 (Paralytics)]\n"
            selected_para = []
            for child in self.ids.drug_choices_para.children[::-1]:
                if hasattr(child, 'cb') and child.cb.active:
                    selected_para.append(child.lbl.text)
                    
            for drug in selected_para:
                if drug == "Succinylcholine":
                    res += f"● {drug}: {1.5 * wt:.1f} mg\n  備註: Onset 45-60s. 注意高血鉀禁忌。\n"
                elif drug == "Rocuronium":
                    res += f"● {drug}: {1.2 * wt:.1f} mg\n  備註: Onset 60s. RSI 首選肌鬆劑。\n"
            
            self.ids.result_label.text = res
        except:
            self.ids.result_label.text = "錯誤: 請檢查輸入數值"

class ABXScreen(Screen):
    def on_enter(self):
        # Initial population of drug list
        self.ids.drug_list.clear_widgets()
        for drug in MedicalData.ABX_GUIDE:
            btn = Button(text=drug['name'], size_hint_y=None, height=dp(50))
            btn.bind(on_release=lambda x, d=drug: self.show_detail(d))
            self.ids.drug_list.add_widget(btn)

    def calculate_egfr(self):
        try:
            age = float(self.ids.age.text)
            wt = float(self.ids.weight.text)
            scr = float(self.ids.scr.text)
            is_male = self.ids.gender_m.active
            
            egfr = ((140 - age) * wt) / (72 * scr)
            if not is_male:
                egfr *= 0.85
                
            self.curr_egfr = egfr
            gender_str = "男" if is_male else "女"
            self.ids.egfr_res.text = f"eGFR: {egfr:.1f} mL/min (CG, {gender_str})"
            
            self.ids.drug_list.clear_widgets()
            for drug in MedicalData.ABX_GUIDE:
                btn = Button(text=drug['name'], size_hint_y=None, height=dp(50))
                btn.bind(on_release=lambda x, d=drug: self.show_detail(d))
                self.ids.drug_list.add_widget(btn)
        except:
            self.ids.egfr_res.text = "錯誤: 請檢查輸入"

    def show_detail(self, drug):
        res = f"【{drug['name']}】\n"
        if drug.get('no_adj'):
            res += "✅ 不需要根據腎功能調整。\n"
        else:
            egfr = self.curr_egfr
            found = None
            for rule in drug['rules']:
                mi = rule.get('min', -1)
                ma = rule.get('max', 9999)
                if egfr >= mi and egfr <= ma:
                    found = rule
                    break
            if found:
                res += f"🚩 當前建議: {found['dose']}\n\n"
            
            res += "【劑量對照表】\n"
            for r in drug['rules']:
                mi = r.get('min', '--')
                ma = r.get('max', '--')
                res += f"• eGFR {mi}-{ma}: {r['dose']}\n"
        
        if drug.get('notes'):
            res += f"\n💡 備註: {drug['notes']}"
            
        p = Factory.DrugDetailPopup()
        p.ids.detail_text.text = res
        p.open()

class PDScreen(Screen):
    def on_enter(self):
        self.ids.drug_choices.clear_widgets()
        
        drugs = ["Cefazolin", "Ceftazidime", "Vancomycin", "Gentamicin", "Amikacin", "Meropenem"]
        for drug in drugs:
            row = Factory.SelectionRow()
            cb = CheckBox(size_hint_x=None, width=dp(50), color=(0.2, 0.6, 1, 1))
            lbl = Label(text=drug, color=(0,0,0,1), halign='left', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            row.add_widget(cb)
            row.add_widget(lbl)
            
            # Store references
            row.cb = cb
            row.lbl = lbl
            
            # Toggle checkbox on release
            row.bind(on_release=lambda x: setattr(cb, 'active', not cb.active))
            
            self.ids.drug_choices.add_widget(row)

    def calculate(self):
        try:
            wt = float(self.ids.pd_weight.ids.ti.text)
            vol = float(self.ids.pd_vol.ids.ti.text)
            mode = self.ids.pd_mode.text
            is_cont = "連續" in mode
            
            res = f"【PD 建議劑量 ({mode})】\n體重: {wt}kg, 單包: {vol}L\n"
            res += "-"*30 + "\n"
            
            for child in self.ids.drug_choices.children[::-1]:
                if hasattr(child, 'cb') and child.cb.active:
                    drug = child.lbl.text
                    if drug == "Cefazolin" or drug == "Ceftazidime":
                        ld, md = (500*vol, 125*vol) if is_cont else (15*wt, 1000)
                        res += f"● {drug}:\n  LD: {ld:.0f}mg, MD: {md:.0f}mg\n"
                    elif drug == "Vancomycin":
                        ld, md = (1000*vol, 25*vol) if is_cont else (30*wt, 15*wt)
                        res += f"● {drug}:\n  LD: {ld:.0f}mg, MD: {md:.0f}mg\n"
                    elif drug == "Gentamicin" or drug == "Amikacin":
                        res += f"● {drug}:\n  MD: {0.6*wt if is_cont else 2.0*wt:.1f}mg\n"
                    elif drug == "Meropenem":
                        res += f"● {drug}:\n  MD: {125*vol if is_cont else 250*vol:.0f}mg\n"
            
            self.ids.pd_res.text = res
        except:
            self.ids.pd_res.text = "錯誤: 參數無效"

class VancoScreen(Screen):
    def calculate(self):
        try:
            w = float(self.ids.w.text)
            h = float(self.ids.h.text)
            a = float(self.ids.a.text)
            s = float(self.ids.s.text)
            is_male = self.ids.v_male.active
            
            crcl = ((140 - a) * w) / (72 * s)
            if not is_male: crcl *= 0.85
            
            ld = round((25 * w) / 250) * 250
            md = round((15 * w) / 250) * 250
            
            if crcl >= 90: freq = "q8-12h"
            elif crcl >= 60: freq = "q12h"
            elif crcl >= 40: freq = "q24h"
            else: freq = "Dose by levels"
            
            res = f"📊 Vancomycin 評估 ({'男' if is_male else '女'})\n"
            res += f"- eGFR: {crcl:.1f} mL/min\n"
            res += "-"*30 + "\n"
            res += f"🚩 建議 Loading: {ld} mg\n"
            res += f"🚩 建議 維持: {md} mg {freq}\n\n"
            res += "⚠️ Trough 目標: 15-20 (重症)"
            self.ids.res.text = res
        except:
            self.ids.res.text = "錯誤"

class AminoScreen(Screen):
    def calculate(self):
        try:
            w = float(self.ids.w.ids.ti.text)
            h = float(self.ids.h.ids.ti.text)
            drug = self.ids.am_drug.text
            is_male = self.ids.am_male.active
            
            # IBW
            base = 50 if is_male else 45.5
            ibw = base + 2.3 * ((h/2.54) - 60)
            target_w = ibw + 0.4*(w-ibw) if w > 1.2*ibw else w
            
            dose_val = 15 if drug == 'Amikacin' else 7
            dose = target_w * dose_val
            
            res = f"🧪 {drug} HDEI ({dose_val}mg/kg)\n"
            res += f"性別: {'男' if is_male else '女'}, IBW: {ibw:.1f}kg\n"
            res += f"基準體重: {target_w:.1f}kg\n"
            res += f"總劑量: {dose:.0f} mg\n\n"
            res += "💡 建議頻率: Q24H (Hartford Nomogram)"
            self.ids.res.text = res
        except:
            self.ids.res.text = "錯誤"

class PJPScreen(Screen):
    def calculate(self):
        try:
            wt = float(self.ids.w.text)
            age = float(self.ids.age.text)
            scr = float(self.ids.scr.text)
            is_male = self.ids.pjp_male.active
            dialysis = self.ids.pjp_dialysis.text
            is_hd = "HD" in dialysis
            
            egfr = ((140 - age) * wt) / (72 * scr)
            if not is_male: egfr *= 0.85
            
            res = ""
            if is_hd:
                res += f"💊 PJP 治療建議 (患者進行血液透析 HD)\n"
                crcl_cat = "HD"
            else:
                res += f"💊 PJP 治療建議 (體重 {wt}kg, eGFR {egfr:.1f} mL/min)\n"
                if egfr > 30: crcl_cat = ">30"
                elif 10 <= egfr <= 30: crcl_cat = "10-30"
                else: crcl_cat = "<10"
            
            res += "-"*30 + "\n"
            daily_range = (12 * wt, 15 * wt)
            infusion_time = 4.0

            def get_dose_info(tmp_range, times, label):
                low_tmp = tmp_range[0] / times
                high_tmp = tmp_range[1] / times
                
                low_amps = min(3.0, low_tmp / 80)
                high_amps = min(3.0, high_tmp / 80)
                
                low_tmp = low_amps * 80
                high_tmp = high_amps * 80
                
                combos_min = self._get_all_vial_combinations(low_amps)
                combos_max = self._get_all_vial_combinations(high_amps)
                
                def format_block(combos, title):
                    if not combos: return f"   [{title}泡製]: N/A\n"
                    best = combos[0]
                    line = f"   ⭐ {title}: {self._format_vial_combination_complex(best)}"
                    return f"   {line}\n"

                block = format_block(combos_min, f"低標 {label}")
                if low_amps != high_amps:
                    block += format_block(combos_max, f"高標 {label}")
                
                rate = f"{(combos_min[0]['volume']/infusion_time):.1f} - {(combos_max[0]['volume']/infusion_time):.1f}" if combos_min and combos_max else "---"
                return {
                    "tmp": f"{low_tmp:.0f}-{high_tmp:.0f} mg",
                    "amps": f"{low_amps:.1f}-{high_amps:.1f} 支",
                    "rate": rate,
                    "block": block
                }

            if crcl_cat == ">30":
                res += f"👉 eGFR > 30 (一般劑量)：\n"
                res += f"每日 TMP 總量 (12-15 mg/kg): {daily_range[0]:.0f}-{daily_range[1]:.0f} mg\n\n"
                q6 = get_dose_info(daily_range, 4, "Q6H")
                res += f"🕒 Q6H:\n  • 每劑: {q6['tmp']} ({q6['amps']})\n  • ⚡ 建議流速: {q6['rate']} mL/hr\n{q6['block']}\n"
            elif crcl_cat == "10-30":
                q12 = get_dose_info((5*wt, 5*wt), 1, "Q12H")
                res += f"👉 eGFR 10-30 (腎修剪)：\n建議 5 mg/kg Q12H\n"
                res += f"  • 每劑: {q12['tmp']} ({q12['amps']})\n  • ⚡ 建議流速: {q12['rate']} mL/hr\n{q12['block']}\n"
            else: # < 10 or HD
                q24 = get_dose_info((5*wt, 5*wt), 1, "Q24H")
                res += f"👉 eGFR < 10 或 HD：\n建議 5 mg/kg Q24H (HD後給藥)\n"
                res += f"  • 每劑: {q24['tmp']} ({q24['amps']})\n  • ⚡ 建議流速: {q24['rate']} mL/hr\n{q24['block']}\n"

            res += "🗓️ HIV: 21天 | 非HIV: 14-21天\n"
            res += "🎚️ 類固醇 (PaO2 < 70):\n"
            res += "Day 1-5: 40mg BID | 6-10: 40mg QD | 11-21: 20mg QD\n"
            res += "⚠️ 嚴禁混藥，輸注 4 小時。"
            self.ids.res.text = res
        except Exception as e:
            self.ids.res.text = f"錯誤: {str(e)}"

    def _get_all_vial_combinations(self, target_vials_float):
        target_ceil = math.ceil(target_vials_float)
        if target_ceil <= 0: return []
        results = []
        def find_combos(remaining, current_combo):
            if remaining == 0:
                results.append(list(current_combo))
                return
            if remaining < 0: return
            start = current_combo[-1] if current_combo else 1
            for i in range(start, 4):
                current_combo.append(i)
                find_combos(remaining - i, current_combo)
                current_combo.pop()
        find_combos(target_ceil, [])
        processed = []
        for raw_combo in results:
            diff = target_ceil - target_vials_float
            combo = [float(x) for x in raw_combo]
            combo[-1] = round(combo[-1] - diff, 1)
            vol = 0
            for x in raw_combo:
                if x == 1: vol += 125
                elif x == 2: vol += 250
                elif x == 3: vol += 500
            processed.append({"combo": combo, "volume": vol, "bags": len(combo)})
        processed.sort(key=lambda x: (x['bags'], x['volume']))
        return processed

    def _format_vial_combination_complex(self, combo_dict):
        combo = combo_dict['combo']
        parts = []
        for vials in combo:
            bag_size = math.ceil(vials)
            vol = 125 if bag_size == 1 else (250 if bag_size == 2 else 500)
            parts.append(f"({vials}支/{vol}mL)")
        return " + ".join(parts)

class HypoNaScreen(Screen):
    def calculate(self):
        try:
            wt = float(self.ids.w.text)
            age = float(self.ids.age.text)
            curr_na = float(self.ids.na.text)
            is_male = self.ids.na_male.active
            fluid = self.ids.fluid_spinner.text
            
            # TBW Estimation
            if is_male:
                coeff = 0.5 if age >= 65 else 0.6
            else:
                coeff = 0.45 if age >= 65 else 0.5
            tbw = wt * coeff
            
            # Infusate Na value
            if "3%" in fluid: inf_na = 513
            elif "0.9%" in fluid: inf_na = 154
            elif "0.45%" in fluid: inf_na = 77
            else: inf_na = 0
            
            # Adrogue-Madias Formula
            change_per_liter = (inf_na - curr_na) / (tbw + 1)
            
            res = f"📊 低血鈉校正分析 (Hyponatremia)\n"
            res += f"- TBW 預估: {tbw:.1f} L (係數: {coeff})\n"
            res += f"- 每 1L 輸液後血鈉變化: {change_per_liter:+.1f} mEq/L\n"
            res += "="*30 + "\n"
            
            res += "🚨 急救建議 (Severe Symptoms)：\n"
            res += "  • 3% NaCl 100mL IV (10-15 mins)\n"
            res += "  • 若未改善，10min 後可重疊，最多給 3 劑。\n\n"
            
            res += "⚠️ 24h 校正上限：\n"
            res += "  • 高風險 (肝損, 酗酒): 8 mEq/L\n"
            res += "  • 一般病患: 10-12 mEq/L (48h 18 mEq/L)\n"
            res += "-"*30 + "\n"
            
            if change_per_liter > 0:
                vol_for_4 = (4.0 / change_per_liter) * 1000
                vol_for_8 = (8.0 / change_per_liter) * 1000
                
                res += f"🎯 目標 +4 mEq/L (安全初始目標):\n"
                res += f"  需要量: {vol_for_4:.0f} mL\n"
                res += f"  ⚡ 建議流速 (4h 達成): {vol_for_4/4:.0f} mL/hr\n\n"
                
                res += f"🎯 目標 +8 mEq/L (24h 上限):\n"
                res += f"  需要量: {vol_for_8:.0f} mL\n"
                res += f"  ⚡ 建議流速 (24h 給予): {vol_for_8/24:.0f} mL/hr"
            else:
                res += "⚠️ 警告: 所選溶液無法提升血鈉。"
                
            self.ids.res.text = res
        except Exception as e:
            self.ids.res.text = f"錯誤: {str(e)}"

class DrugScreen(Screen):
    def on_enter(self):
        self.filter_drugs(self.ids.search.text)

    def filter_drugs(self, query):
        self.ids.drug_list.clear_widgets()
        for drug in MedicalData.DRUG_STABILITY:
            if query.lower() in drug['name'].lower():
                btn = Button(text=drug['name'], size_hint_y=None, height=dp(50))
                btn.bind(on_release=lambda x, d=drug: self.show_detail(d))
                self.ids.drug_list.add_widget(btn)

    def show_detail(self, drug):
        self.current_drug = drug
        popup = Factory.TitrationPopup()
        popup.calc_inputs = {}

        info = f"【{drug['name']}】\n"
        info += f"貯存: {drug['storage']}\n"
        info += f"安定性: {drug['stability']}\n"
        info += f"泡製: {drug['prep']}\n"
        info += f"Bolus/Rate: {drug['bolus']} / {drug['rate']}"
        popup.ids.info_text.text = info

        grid = popup.ids.inputs_grid
        is_undiluted = "undilute" in drug.get('prep', "").lower()

        if not is_undiluted and drug.get('calc'):
            c = drug['calc']
            self._add_row(grid, popup, "體重 (kg):", "70", "wt", "titrate")
            self._add_row(grid, popup, f"目標劑量 ({c['unit']}):", str(c.get('def_dose', 5)), "dose", "titrate")
            self._add_row(grid, popup, "藥物含量 (mg/mcg/U):", str(c['amt']), "amt", "titrate")
            self._add_row(grid, popup, "稀釋體積 (mL):", str(c['vol']), "vol", "titrate")
            self._calc_titrate(popup)
        elif not is_undiluted and drug.get('rate') != "--":
            import re
            vm = re.search(r'(\d+)\s*mL', drug['prep']); vol = vm.group(1) if vm else "500"
            rm = re.search(r'(\d+)\s*mL/hr', drug['rate']); rate = rm.group(1) if rm else "20"
            self._add_row(grid, popup, "輸注體積 (mL):", vol, "s_vol", "simple")
            self._add_row(grid, popup, "流速 (mL/hr):", rate, "s_rate", "simple")
            self._calc_simple(popup)
        else:
            popup.ids.result_label.text = "(此藥直接給予，無需稀釋計算)"

        popup.open()

    def _add_row(self, grid, popup, label, default, key, mode):
        grid.add_widget(Label(text=label, color=(1, 1, 1, 1), size_hint_y=None, height=dp(40)))
        ti = TextInput(text=default, multiline=False, size_hint_y=None, height=dp(40), input_filter='float')
        popup.calc_inputs[key] = ti
        def _on_change(inst, val, p=popup, m=mode):
            if m == "titrate": self._calc_titrate(p)
            else: self._calc_simple(p)
        ti.bind(text=_on_change)
        grid.add_widget(ti)

    def _calc_titrate(self, popup):
        try:
            i = popup.calc_inputs
            wt = float(i['wt'].text); dose = float(i['dose'].text)
            amt = float(i['amt'].text); vol = float(i['vol'].text)
            c = self.current_drug['calc']
            if amt <= 0 or vol <= 0: return
            t = c['type']
            if t == 'mcg': r = (dose * wt * 60 * vol) / (amt * 1000)
            elif t == 'mg': r = (dose * wt * vol) / amt
            elif t == 'U': r = (dose * wt * vol) / amt
            elif t == 'mcg_fixed': r = (dose * 60 * vol) / (amt * 1000)
            elif t == 'U_fixed': r = (dose * 60 * vol) / amt
            else: r = 0
            popup.ids.result_label.text = f"建議流速: {r:.1f} mL/hr"
        except:
            popup.ids.result_label.text = "請輸入正確數值"

    def _calc_simple(self, popup):
        try:
            i = popup.calc_inputs
            vol = float(i['s_vol'].text); rate = float(i['s_rate'].text)
            if rate > 0:
                popup.ids.result_label.text = f"預計輸注時間: {vol/rate:.1f} 小時"
        except:
            popup.ids.result_label.text = "請輸入正確數值"


class MedCalcApp(App):
    def build(self):
        return Builder.load_string(KV)

if __name__ == '__main__':
    MedCalcApp().run()
