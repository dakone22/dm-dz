from zlib import compress
import base64
import string

URL = 'https://www.plantuml.com/plantuml/png/'

plantuml_alphabet = string.digits + string.ascii_uppercase + string.ascii_lowercase + '-_'
base64_alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits + '+/'
b64_to_plantuml = bytes.maketrans(base64_alphabet.encode('utf-8'), plantuml_alphabet.encode('utf-8'))


class Output:
    def __init__(self):
        self.markdown_text = ''
        self.text("""<style type="text/css"> img {height: 250px;}</style>""")
    
    def text(self, markdown_text, end='\n'):
        self.markdown_text += markdown_text + end
    
    def math(self, math_text, end='\n'):
        self.markdown_text += f"$${math_text}$$" + end
    
    def image(self, url, text='', end='\n'):
        self.markdown_text += f"![{text}]({url})" + end
    
    def get_text(self):
        return self.markdown_text

    def print(self):
        try:
            from IPython.display import Markdown as print_markdown
        except ImportError:
            print_markdown = print
        print_markdown(self.markdown_text)


def deflate_and_encode(plantuml_text):
    """zlib compress the plantuml text and encode it for the plantuml server."""
    zlibbed_str = compress(plantuml_text.encode('utf-8'))
    compressed_string = zlibbed_str[2:-4]
    return base64.b64encode(compressed_string).translate(b64_to_plantuml).decode('utf-8')


def build_graph(graph, marked_vertex=None, footer=""):
    if marked_vertex is None:
        marked_vertex = {}

    definition = [f'() "<latex>x_{i}</latex>" as x{i}' if i not in marked_vertex else f'() "<latex>x_{i} ({marked_vertex[i]})</latex>" as x{i} #pink;line:red;line.bold;text:red' for i in sorted(graph.keys())]

    x = []
    for start, xxx in graph.items():
        for to, flow in xxx.items():
            if flow.value < flow.max_value:
                x.append(f"x{start} --> x{to} : {flow.value} / {flow.max_value}")
            else:
                x.append(f"x{start} --> x{to} #line:red;line.bold;text:red : {flow.value} / {flow.max_value}")
    
    return "@startuml\n"\
           "left to right direction\n"\
           f'footer "{footer}"\n' + \
           '\n'.join(definition) + '\n' + \
           '\n'.join(x) + \
           '\n@enduml'


def get_url(plantuml_text, url=URL):
    return url + deflate_and_encode(plantuml_text)
