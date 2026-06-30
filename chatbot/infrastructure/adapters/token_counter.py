import os
from tokenizers import Tokenizer
from chatbot.application.ports import TokenCounterPort
from chatbot.domain.message import Message


class TokenizerCounterAdapter(TokenCounterPort):

    def __init__(
        self,
        tokenizer_path: str | None = None
    ) -> None:
        if tokenizer_path is None:
            tokenizer_path = os.path.join(
                os.path.dirname(__file__),
                "tokenizer_files",
                "tokenizer.json",
            )
        self._tokenizer: Tokenizer = Tokenizer.from_file(tokenizer_path)

    def count(self, messages: list[Message]) -> int:
        total = 0

        for msg in messages:
            d = msg.to_dict()
            # Tokens extras para tags y limites de mensajes
            total += 5

            content = d.get("content", "")
            if content:
                total += len(self._tokenizer.encode(content))

            # Resultados de llamadas a herramientas agrupados
            # Se cuentan los tokens de los resultados
            if d.get("tool_results"):
                for tr in d["tool_results"]:
                    total += len(self._tokenizer.encode(tr.get("content", "")))

            # Llamadas a herramientas y tokens extras
            if d.get("tool_calls"):
                for tc in d["tool_calls"]:
                    func = tc.get("function", {})
                    total += len(
                        self._tokenizer.encode(func.get("name", ""))
                    )
                    total += len(
                        self._tokenizer.encode(str(func.get("arguments", "")))
                    )
        # Cantidad de tokens añadidos para manejar la preparación de la respuesta del asistente
        total += 3

        return total
