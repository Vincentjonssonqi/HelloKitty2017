import sys
class Printer:
    
    def __init__(self):
        self.count = 0
        self.lines = {}
    def add(self,name,content):
        self.lines[name]={
                "line_number":self.count,
                "content":content
            }
        sys.stdout.write("{}\n".format(content))
        sys.stdout.flush()
        self.count += 1
    def replace(self,name,content):
        from_cursor_to_content = self.count - self.lines.get(name).get("line_number")
        self.lines[name]["content"] = content
        for i in range(from_cursor_to_content):
            sys.stdout.write("\033[F") #back to previous line
            sys.stdout.flush()
        self.remove()
        sys.stdout.write(content)
        for i in range(from_cursor_to_content + 1):
            sys.stdout.write("\033[B") #forward to the next line
            sys.stdout.flush()
        
    def remove(self):
        sys.stdout.write("\033[K") #clear line
        sys.stdout.flush()
            
