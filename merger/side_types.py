from collections import OrderedDict

business = [ 'בע"מ', "INC", "LTD", "בנק" ,"ביטוח",
" ושות'",
"חברה",
" בעמ"
" בע\"מ",
"שותפות מוגבלת",
"חברת",
"חב' ",
"עורכי דין",
"רואי חשבון",
"investments",
"company",
"limited",
"l.t.d",
"corp",
"GMBH",
"group",
]



government = [
"מדינת ישראל",
"מקרקעי ישראל" ,
"משרד הפנים",
"משרד האוצר",
"משרד התחבורה",
"משרד הקליטה",
"משרד העלייה",
"רשות המיסים" ,
"המוסד לביטוח לאומי" ,
"ביטוח לאומי",
"משרד הבינוי",
"משרד השיכון" ,
"משרד הבינוי",
"משרד החקלאות",
"היועץ המשפטי לממשלה",
"משרד החינוך",
'שב"ס',
"בתי הסוהר",
"נציב שירות" ,
"קצין משטרה",
"משרד לביטחון פנים",
"שר האוצר",
"שר הבטחון",
"שר ביטחון",
"משרד התרבות" ,
"משרד הרווחה",
"משרד הבריאות",
"מבקר המדינה",
"ממשלת ישראל",
"משטרת ישראל",
"המשטרה",
"ראש הממשלה" ,
"משרד הביטחון" ,
"משרד האנרגיה",
"משרד החוץ",
"משרד המשפטים",
"רשות האוכלוסין",
"משרד התיירות",
"משרד התעשייה",
    "שר החינוך"
"משרד הבטחון",
"הכנסת",
    "כנסת ישראל",
"שר הפנים",
"רשות הטבע והגנים",
"לשכת עוה",
"המרכז לגביית קנסות",
"כונס הנכסים הרשמי",
"המועצה לשידורי כבלים ולווין",
"פקיד שומה",
"פקידת שומה",
"פקיד השומה",
"פקידת השומה",
"כונס הנכסים הרשמי",
"המועצה הדתית אילת",
"כונס הנכסים הרישמי",
"בתי סוהר",
    "בית סוהר",
    "בתי הסהר",
    "בתי הסוהר",
"פיקוח על הבניה",
"הועדה המקומית",
" לתכנון ולבניה",
"משרד מיסוי מקרקעין",
"שר הפנים",
"הרבנות ה",
"לשכת עורכי הדין",
"השר לשירותי דת",
"המנהל האזרחי",
"כונס הנכסים הרישמי",
"משרד הבטחון",
"לתכנון ובניה",
"סגן שר ה",
"מועצת התכנון העליונה",
"מדינת שיראל",
"ועדת הבחירות",
"ועדת העררים",
"מנהל מיסוי מקרקעין",
"נכסי נפקדים",
"כונס הנכסים הרשמי",
    
"אגף המכס",
"המשרד להגנת",
"האפוטרופוס הכללי",
"הוועדה המחוזית",
"הוועדה המיוחדת",
"הועדה המיוחדת",
"המשרד לבטחון פנים",
"המשרד לענייני",
"הסוכנות היהודית",
"הרשות לשמירת הטבע",
"ועדת ",
"הרשות",
"מנהל מיסוי",
"מנהל מס",
"רשות שדות התעופה",
"קרן קיימת לישראל",
"שירותי בריאות כללית",
"הסנגוריה הציבורית",
]

nogov = [
"ועד בית הכנסת",
"ערוץ הכנסת",
"ערוץ לשידורי הכנסת",
"עמותת בית הכנסת",
"קצין",
"התגמולים"]

judiciary = [
"בית המשפט",
'ביהמ"ש',
'בימ"ש',
"בית משפט" ,
"בית הדין" ,
"בית דין",
'ביה"ד',
'בי"ד',
"השופט",
"השופטת",
"הדיין"]

military = [
"המפקד",
"מפקד" ,
"מתאם הפעולות" ,
"מתאם פעולות" ,'שב"כ'
,"שירות הביטחון" ,
"ראש המנהל האזרחי",
"היועץ המשפטי לגדה" ,
"הצבא",
"צבאי",
'צה"ל',
'שירות הבטחון']

municipality = [
"עריית" ,
"עיריית",
"מועצת איזורית" ,
"מועצה כפרית",
"המועצה המקומית",
"מועצת הכפר",
"המועצה האזורית",
"מועצה אזורית"
,"מועצה האזורית"
,"הוועדה המקומית"
,"הועדה המקומית"
,"וועדה מקומית"
,"ועדה מקומית"
,"מושב עובדים"
,"ועד מקומי"
,"וועד מקומי"
,"המועצה הדתית "
,"המועצה המקומית "
,"מושב שיתופי"
,"כפר שיתופי"
,"מועצת העיר "
,"קיבוץ"
,"ראש מועצת"
,"המועצה האזורית"
]

NGO =[
"עמותת",
'ע"ר',
"האגודה",
"אגודה",
"המוקד להגנת הפרט",
'חל"צ' ,
"תנועת רגבים",
"מסדר הכרמליתים היחפים",
"המוקד לפליטים ומהגרים",
"התנועה למשילות ודמוקרטיה",
"הפורום הישראלי לאנרגיה",
"צלול עמותה לאיכות הסביבה",
"עורכי הדין לקידום מנהל תקין",
"התנועה למען איכות השלטון בישראל",
"ועדת המעקב העליונה לענייני הערבים בישראל",
    
"אגודת",
"ארגון",
"אירגון הארגון",
"העמות",
"עמותה",
"התאחדות",
"ההתאחדו",
"תנוע",
"האיגו",
"רגבי",
"חוג",
"הוועד הציבורי",
"הסתדרות העובדי",
"הפורו",
"התנועה",
"אדם טבע ודי",
"תנו לחיות לחיו",
"המוקד",
"אגודה שיתופית חקלאי",
"החברה להגנת הטב",
"בית הספר התיכו",
"המכלל",
"מכלל",
"ישיב",
"המרכז האקדמ",
"האוניברסיט",
"מרכז השלטון המקומי",
"מפלגת",
"המפלגה",
"בית הכנסת"
]

individual = [
"עזבון המנוח",
"עזבון המנוחה",
"עיזבון המנוח",
"עיזבון המנוחה",
"ואח'",
"ואחרים",
"ד\"ר",
"פרופ'",
"ז\"ל",
"יורשי המנוח",
"יורשי המנוחה",
"העיזבון",
"בני משפחת",
"המנוח"
]

the_map = OrderedDict()
the_map [ 'Government'] = government
the_map ['Business'] = business
the_map ['Judiciary'] = judiciary
the_map ['Military'] = military
the_map['Municipal'] = municipality
the_map['NGO'] = NGO
the_map["Individual"] = individual

def is_no_gov(x):
    for n in nogov:
        if n in x:
            return True
    return False

def is_arab(x):
    from baguette.merger.arab_names import arab_names
    words = x.split()
    for w in words:
        if w in arab_names:
            return True
    return False

def get_side_type(t):
    if not t:
        return ''
    for k, patterns in the_map.items():
        for p in patterns:
            if p in t or p.lower() in t.lower():
                return k

    govstart = ['שר ה', 'משרד ה', 'שרת ה','משרד ה', 'סגן שר ה',
                'סגנית שר ה', 'רשות ה','הרשות ה', 'השר ל',
                'השרה ל']
    for g in govstart:
        if t.startswith(g) and not is_no_gov(t):
            return 'Government'
    cleansed = [x for x in t.split() if x.strip()]
    if len(cleansed) in [2,3]:
        return "Individual"
    if is_arab(t):
        return "Individual"
    return ""