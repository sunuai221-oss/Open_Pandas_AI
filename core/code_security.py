import ast

DANGEROUS_NODES = (
    ast.Import,
    ast.ImportFrom,
    ast.Global,
    ast.With,
    ast.AsyncWith,
)

DANGEROUS_FUNCTIONS = {
    'open', 'exec', 'eval', 'compile', 'os', 'sys', 'subprocess', 'shutil',
    'socket', 'requests', 'input', '__import__', 'exit', 'quit'
}

DANGEROUS_NAMES = {
    '__builtins__', '__import__', 'globals', 'locals', 'vars', 'eval', 'exec', 'open', 'compile'
}

DANGEROUS_ATTRIBUTES = {
    '__class__', '__dict__', '__getattribute__', '__globals__', '__mro__',
    '__subclasses__', '__base__', '__bases__'
}

def is_code_safe(code: str) -> (bool, str):
    """
    Analyse le code genere via AST, bloque imports, acces systeme/reseau, introspection dangereuse.
    Retourne (True, "") si OK, sinon (False, raison).
    """
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, DANGEROUS_NODES):
                return False, f"Code interdit: usage de {type(node).__name__}"
            if isinstance(node, ast.Name) and node.id in DANGEROUS_NAMES:
                return False, f"Reference interdite au symbole: {node.id}"
            if isinstance(node, ast.Attribute) and node.attr in DANGEROUS_ATTRIBUTES:
                return False, f"Attribut interdit detecte: {node.attr}"
            if isinstance(node, ast.Call):
                func = getattr(node.func, 'id', None)
                attr = getattr(node.func, 'attr', None)
                if func in DANGEROUS_FUNCTIONS:
                    return False, f"Appel interdit a la fonction: {func}"
                if attr in DANGEROUS_FUNCTIONS:
                    return False, f"Appel interdit a l'attribut: {attr}"
    except Exception as e:
        return False, f"Erreur lors de l'analyse de securite: {str(e)}"
    return True, ''
