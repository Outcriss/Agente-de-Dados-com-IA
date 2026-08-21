import os
import re
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

MODEL = "gemini-3.6-flash"
CSV_PATH = "data/vendas_exemplo.csv"
OUTPUT_DIR = "outputs"

SYSTEM_PROMPT_TEMPLATE = """Você é um assistente de análise de dados que escreve código Python usando Pandas para responder perguntas sobre um DataFrame chamado `df` já carregado em memória.

Esquema do DataFrame:
{schema}

Regras:
- Responda APENAS com um bloco de código Python dentro de ```python ... ```, sem nenhuma explicação antes ou depois do bloco.
- Use apenas o que já está disponível: `df` (pandas.DataFrame), `pd` (pandas), `plt` (matplotlib.pyplot) e a função `salvar_grafico(nome_arquivo)`.
- Ao final do código, atribua a resposta da pergunta (texto, número, lista ou DataFrame) à variável `resultado`.
- Se a pergunta pedir um gráfico/visualização, crie o gráfico com matplotlib e chame `salvar_grafico("nome_do_arquivo.png")` para salvá-lo em outputs/. Não chame plt.show().
- Não invente colunas que não existem no esquema acima.
- Não use imports adicionais, leitura/escrita de arquivos, comandos de sistema ou de rede.
"""

CODE_BLOCK_RE = re.compile(r"```(?:python)?\s*(.*?)```", re.DOTALL)


class DataAgent:
    def __init__(self, csv_path: str = CSV_PATH, output_dir: str = OUTPUT_DIR):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY não encontrada no arquivo .env")

        self.client = genai.Client(api_key=api_key)
        self.csv_path = csv_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.df = pd.read_csv(csv_path, parse_dates=["data"])

    def _descrever_esquema(self) -> str:
        colunas = [f"- {col} ({dtype})" for col, dtype in self.df.dtypes.items()]
        exemplo = self.df.head(3).to_string(index=False)
        return (
            "Colunas:\n" + "\n".join(colunas)
            + f"\n\nTotal de linhas: {len(self.df)}"
            + f"\n\nExemplo de dados:\n{exemplo}"
        )

    def _gerar_codigo(self, pergunta: str) -> str | None:
        system = SYSTEM_PROMPT_TEMPLATE.format(schema=self._descrever_esquema())
        try:
            response = self.client.models.generate_content(
                model=MODEL,
                contents=pergunta,
                config=types.GenerateContentConfig(system_instruction=system),
            )
        except errors.APIError as e:
            print(f"Erro na chamada à API Gemini (código {e.code}): {e.message}")
            return None

        texto = response.text or ""
        match = CODE_BLOCK_RE.search(texto)
        if not match:
            print(f"A API não retornou um bloco de código válido:\n{texto}")
            return None
        return match.group(1).strip()

    def _salvar_grafico(self, nome_arquivo: str) -> str:
        caminho = self.output_dir / nome_arquivo
        plt.savefig(caminho, bbox_inches="tight")
        plt.close("all")
        print(f"Gráfico salvo em: {caminho}")
        return str(caminho)

    def _executar_codigo(self, codigo: str):
        namespace = {
            "df": self.df,
            "pd": pd,
            "plt": plt,
            "salvar_grafico": self._salvar_grafico,
        }
        exec(codigo, namespace)
        return namespace.get("resultado")

    def perguntar(self, pergunta: str):
        codigo = self._gerar_codigo(pergunta)
        if codigo is None:
            return None
        print("\nCódigo gerado:\n" + codigo)
        try:
            resultado = self._executar_codigo(codigo)
        except Exception as exc:
            print(f"\nErro ao executar o código gerado: {exc}")
            return None
        if resultado is not None:
            print("\nResultado:")
            print(resultado)
        return resultado


def main():
    agente = DataAgent()
    print("Agente de Dados pronto. Digite sua pergunta sobre as vendas (ou 'sair' para encerrar).")
    while True:
        pergunta = input("\nPergunta: ").strip()
        if pergunta.lower() in {"sair", "exit", "quit"}:
            break
        if not pergunta:
            continue
        agente.perguntar(pergunta)


if __name__ == "__main__":
    main()
