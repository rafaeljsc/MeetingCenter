import logging

from llm.azure import setup_structured_output_model
from tasks.utils.prompt_schema import AtaModel

logger = logging.getLogger(__name__)


def call_summary(transcript: dict) -> dict | None:
    """Gera uma ata estruturada a partir de um transcript em json.

    Args:
        transcript (dict): Transcript em json da reunião
    """

    ata_model = setup_structured_output_model(AtaModel, temperature=0)

    messages = [
        {
            "role": "system",
            "content": (
                "Você é um assistente que gera uma ata profissional e detalhada de reunião a partir de um transcript em json. "
                "Os participantes da reunião se encontram no topo do json. "
                "Os participantes sempre devem ser mencionados seguidos de suas respectivas empresas. "
                "Consulte a chave 'participants' do json para fazer a correlação 'name (company)'. "
                "A estrutura do transcript é uma lista de dicionários, onde a chave é o nome do participante e o valor, o texto transcrito. "
                "A ata deve ser clara e informativa, principalmente em relação aos temas tratados e compromissos futuros. "
                "Idioma de entrada e saída da ata: pt-br"
            ),
        },
        {"role": "user", "content": "transcript json da reunião"},
        {"role": "user", "content": transcript},
    ]

    try:
        return ata_model.invoke(messages)
    except Exception:
        return None
