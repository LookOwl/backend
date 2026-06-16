class UsuarioNoEncontrado(Exception):
    def __init__(self, identifier: str) -> None:
        super().__init__(f"Usuario '{identifier}' no encontrado")
