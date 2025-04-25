from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
import json, os, re

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.formats = {}
        self.load_colors()
        self.setup_rules()

    def load_colors(self):
        default_colors = {
            "background": "#000000",
            "text": "#FFFFFF",
            "keyword": "#FF6600",
            "builtin": "#FFCC00",
            "string": "#66FF00",
            "comment": "#9933CC",
            "function": "#FFCC00",
            "class": "#FFCC00",
            "def": "#FFCC00",
            "number": "#FF99FF",
            "operator": "#FF6600",
            "brace": "#FFFFFF",
            "decorator": "#FFCC00",
            "punctuation": "#FFFFFF",
            "highlight": "#333333",
            "cursor": "#FFFFFF",
            "selection": "#555555",
            "true_false": "#FFCC00",
            "dot": "#FFCC00",
            "highlight_match": "#7dff64",
            "match_foreground": "#f8f8f2",
            "intent_line": "#242424"
        }
    
        json_path = os.path.join(os.path.dirname(__file__), "/themes/vibrant_ink.json")
        try:
            with open(json_path, "r") as f:
                colors = json.load(f)
        except:
            colors = default_colors
    
        self.background_color = QColor(colors.get("background", "#1E1E1E"))
        self.default_format = QTextCharFormat()
        self.default_format.setForeground(QColor(colors.get("default", "#CCCCCC")))
    
        for key, color in colors.items():
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            self.formats[key] = fmt
    
    def get_loaded_colors(self):
        color_map = {}
        for key, fmt in self.formats.items():
            color_map[key] = fmt.foreground().color().name()
        return color_map
    
    def setup_rules(self):
        self.rules = []

        KEYWORDS = r'\b(?:import|from|as|def|class|return|if|else|elif|while|for|in|try|except|finally|with|pass|break|continue|and|or|not|is|lambda|yield|assert|del|global|nonlocal|raise)\b'
        BUILTINS = r'\b(?:print|len|range|open|input|int|str|list|dict|set|tuple|type|dir|help|isinstance|super|enumerate|zip|map|filter|sum|min|max|abs|round|sorted)\b'
        COMMENTS = r'#.*'
        STRINGS = r'(\'[^\']*\'|"[^"]*")'
        NUMBERS = r'\b\d+(\.\d+)?\b'
        OPERATORS = r'[-+*/%=<>!&|^~]+'
        BRACES = r'[\[\]{}()]'
        CLASS_DEF = r'\bclass\s+\w+'
        DEF_DEF = r'\bdef\s+\w+'
        TRUE_FALSE = r'\b(True|False|None)\b'
        DOT = r'\.'

        self.rules += [
            (KEYWORDS, self.formats["keyword"]),
            (BUILTINS, self.formats["builtin"]),
            (COMMENTS, self.formats["comment"]),
            (STRINGS, self.formats["string"]),
            (NUMBERS, self.formats["number"]),
            (OPERATORS, self.formats["operator"]),
            (BRACES, self.formats["brace"]),
            (CLASS_DEF, self.formats["class"]),
            (DEF_DEF, self.formats["def"]),
            (TRUE_FALSE, self.formats["true_false"]),
            (DOT, self.formats["dot"])
        ]

    def highlightBlock(self, text):
        self.setFormat(0, len(text), self.default_format)  # Fondo predeterminado
    
        for pattern, fmt in self.rules:
            for match in re.finditer(pattern, text):
                start, end = match.span()
                self.setFormat(start, end - start, fmt)
