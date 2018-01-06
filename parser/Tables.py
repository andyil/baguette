

class Tables:

    def __init__(self):
        self.tables = []

    def add(self, table):
        self.tables.append(table)

    def render(self):
        html = "<html>"
        html += '<head><meta charset="UTF-8"><style>.first{background-color:lightblue;}</style></head><body>'
        for t in self.tables:
            html += "<table border=1>"
            first = True
            for row in t:
                key = row[0]
                name = row[1]
                if first:
                    clazz = ' class="first"'
                    first = False
                else:
                    clazz=''
                html +="<tr%s><td>%s</td><td>%s</td></tr>" % (clazz, key, name)
            html += "</table><br/>"

        open("out.html", "w").write(html.encode('utf8'))
