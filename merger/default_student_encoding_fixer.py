from os.path import expanduser, join
from csv import DictReader


all_default = []
fixed = []

def is_problem_present_judge(line, i):
    if f'winner-{i}' not in line:
        print()
    r = line[f'winner-{i}'] == 'Petitioner' and \
        line[f'disposition-{i}'] == 'On the merits' and \
        line[f'outcome-{i}'] == 'No disposition'
    if not r:
        return
    judge = line.get(f'judge-{i}', 'xxxx')
    return judge

def is_problem_present(line):
    r = line['winnercourt'] == 'Petitioner' and \
            line['dispositioncourt'] == 'On the merits' and \
            line['outcomecourt'] == 'No disposition'
    return r

def is_problem_present_all_judges(line):
    for i in range(1, 10):
        judge = is_problem_present_judge(line, i)
        if judge:
            return judge

def has_outcome_winner_issue(line):
    court = f'{line["outcomecourt"]}:{line["winnercourt"]}'
    for ii in range(1, 10):
        judge_key_outcome = f'outcome-{ii}'
        judge_key_winner = f'winner-{ii}'
        judge_result = f'{line[judge_key_outcome]}:{line[judge_key_winner]}'
        if judge_result == court:
            return False
    print(line['casename'])
    return True

def is_problem_present_general(line):
    if has_outcome_winner_issue(line):
        return "no judge picked court's result"
    if is_problem_present(line):
        return "court has defaults"
    j = is_problem_present_all_judges(line)
    if j:
        return f'judge {j} has defaults'



def get_max(line, attribute):
    count = {}
    for i in range(1, 10):
        attribute_name = f'{attribute}-{i}'
        attribute_value = line.get(attribute_name, '')
        if not attribute_value:
            continue
        judge_name = line.get(f'judge-{i}', None)
        if judge_name:
            c = count.setdefault(attribute_value, 0)
            count[attribute_value] = c + 1

    items = list(count.items())
    items.sort(key=lambda x:x[1])
    return items[-1][0]

def fix_default_student_encoding(line):
    global fixed
    if not is_problem_present(line):
        for i in range(1, 10):
            is_problem_present_judge(line, i)
        return
    attrs = ['disposition', 'winner', 'outcome']
    maxs = {f'{attr}court':get_max(line, attr) for attr in attrs}
    if is_problem_present(maxs):
        all_default.append(line['casename'])
        return
    for k, v in maxs.items():
        line[k] = v
    fixed.append(line['casename'])
    return

def print_report():
    global fixed, all_default
    print(f'{len(fixed)} fixed, {len(all_default)} stayed')
    for f in fixed:
        print(f.split()[1])

def issue_fix_documents(documents=[], answers=[]):
    documents_part = '(%s)' % ", ".join(documents)
    print(f'update poorslaves_document set answers=0 where id in {documents_part};')
    answers_part = '(%s)' % ", ".join(answers)
    print(f'update poorslaves_answer set accepted = 0 where id in {answers_part};')

def main():
    K = '\ufeffid'
    bad_documents = set()
    good_documents = set()
    bad_answers = []
    document_by_answer = {}
    reasons = {}
    home = expanduser('~')
    f2 = join(home, 'supreme-court-scrap', 'answers-21.csv')
    with open(f2, 'r', encoding='utf-8') as f:
        d = DictReader(f)
        for line in d:
            answer = line[K]
            document = line['Document']
            document_by_answer[answer] = document
            problem = is_problem_present_general(line)
            if problem:
                bad_documents.add(document)
                bad_answers.append(answer)
                reasons[answer] = problem
            else:
                good_documents.add(document)

    to_fix = bad_documents - good_documents

    print(f'Bad documents {len(bad_documents)}')
    print(f'Good documents {len(good_documents)}')
    print(f'Documents to reset {len(to_fix)}')

    print(f'Answers to invalidate {len(bad_answers)}')
    for k, v in reasons.items():
        print(v)

    issue_fix_documents(to_fix, bad_answers)

if __name__=="__main__":
    main()