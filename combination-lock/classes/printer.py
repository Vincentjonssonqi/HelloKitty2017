import sys
class Printer:

    def __init__(self):
        self.count = 0
        self.lines = {}
    def add(self,name,content,with_name_prefix):
        line={
                "line_number":self.count,
                "content":content,
                "prefix":"{}:\t\t".format(name.upper()) if with_name_prefix else ""
            }
        self.lines[name] = line
        self.print_line(line)
        self.count += 1
    def replace(self,name,content):
        line = self.lines[name]
        from_cursor_to_content = self.count - line.get("line_number")
        line["content"] = content
        #for i in range(from_cursor_to_content):
        #    sys.stdout.write("\033[F") #back to previous line
        #    sys.stdout.flush()
        #self.remove()
        self.print_line(line)
        for i in range(from_cursor_to_content + 1):
            sys.stdout.write("\033[B") #forward to the next line
            sys.stdout.flush()

    def remove(self):
        sys.stdout.write("\033[K") #clear line
        sys.stdout.flush()

    def print_line(self,line):
        sys.stdout.write("\t\t{}{}\n".format(line["prefix"],line["content"]))
        sys.stdout.flush()
