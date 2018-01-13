# -*- coding: utf-8 -*-


issues_types = {
    u"ע\"פ" : "Criminal Appeal",
    u"ע\"א" : "Civil Appeal",
    u"ע\"מ" : "Administrative Appeal",
    u"בג\"ץ" : "High Court of Justice",
    u"עע\"מ" : "Administrative Appeal",
    u"א\"ב" : "Election Approval",
    u"ע\"ב" : "Election Appeal",
    u"דנ\"א" : "Civil Further Hearing",
    u"דנ\"פ" : "Criminal Further Hearing",
    u"דנ\"מ" : "Administrative Further Hearing",
    u"דנג\"ץ" : "High Court of Justice Further Hearing",
    u"מ\"ח" : "Criminal Retrial",

    u"בש\"פ" : "Criminal Request",
    u"בש\"א": "Civil Request",
    u"בש\"מ": "Administrative Request",
    u"בשג\"ץ": "High Court Request",

   u"רע\"פ" : "Criminal Request to Appeal",
    u"רע\"א": "Civil Request to Appeal"

}

interesting_types = {
    u"ע\"פ" : "Criminal Appeal",
    u"ע\"א" : "Civil Appeal",
    u"ע\"מ" : "Administrative Appeal",
    u"בג\"ץ" : "High Court of Justice",
    u"עע\"מ" : "Administrative Appeal",
    u"א\"ב" : "Election Approval",
    u"ע\"ב" : "Election Appeal",
    u"דנ\"א" : "Civil Further Hearing",
    u"דנ\"פ" : "Criminal Further Hearing",
    u"דנ\"מ" : "Administrative Further Hearing",
    u"דנג\"ץ" : "High Court of Justice Further Hearing",
    u"מ\"ח" : "Criminal Retrial"
}

roles = {
    u"מערער": "petitioner",
    u"עותר": "petitioner",
    u"משיב": "respondent",
    u"קשור": "related"
}

decisions = {
    u"החלטה" : "decision",
    u"פסק-דין" : "verdict"
}

judge_honor_title = {
    u"כבוד השופט": {"gender": "male", "english": "Justice"},
    u"כבוד השופטת": {"gender": "female", "english": "Justice"},
    u"כבוד הנשיאה": {"gender": "female", "english": "President"},
    u"כבוד הנשיא": {"gender": "male", "english": "President"},
    u"כבוד המשנה לנשיא": {"gender": "male", "english": "Vice President"},
    u"כבוד המשנָה לנשיא": {"gender": "female", "english": "Vice President"},
    u"כבוד המשנה לנשיאה": {"gender": "male", "english": "Vice President"},
    u"כבוד המשנָה לנשיאה": {"gender": "female", "english": "Vice President"},
    u"כבוד הרשם": {"gender": "male", "english": "rasham"},
    u"כבוד הרשמת": {"gender": "female", "english": "rasham"}
}

retired = u"(בדימ')"

missing_translations = {}

def translate_issue_type(issue_type_hebrew):
    if issue_type_hebrew not in issues_types:
        missing_translations[issue_type_hebrew] = True
        return None
    return issues_types[issue_type_hebrew]

def is_interesting_type(issue_type_hebrew):
    return issue_type_hebrew in interesting_types

def translate_role(hebrew_role):
    if hebrew_role not in roles:
        missing_translations[hebrew_role] = True
        return None
    return roles[hebrew_role]

def translate_decision(hebrew_dec_name):
    if hebrew_dec_name not in decisions:
        missing_translations[hebrew_dec_name] = True
        return None
    return decisions[hebrew_dec_name]

def is_knesset_member(name):
    mks = [u"ח\"כ", u"חה\"כ"]
    for mk in mks:
        if name.startswith(mk):
            return True
    return False