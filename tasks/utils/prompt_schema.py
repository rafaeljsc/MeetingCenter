import logging

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AtaModel(BaseModel):
    goal: str = Field(
        description="Detalhamentos dos principais objetivos identificados",
        examples=[
            "Formalizar la decisión interna de Neosecure de cerrar unilateralmente el proyecto.",
        ],
    )

    topics: list = Field(
        description="Lista de dicionários com os principais temas da reunião. A reunião pode ter um ou vários temas.",
        examples=[
            {
                "topic": "Contratação de novos colaboradores",
                "content": "Durante a reunião, Lucas Martins (Acme) destacou a carência de profissionais...",
            },
        ],
    )

    tasks: list = Field(
        description=(
            "Lista de dicionários com as futuras tasks dos participantes identificados durante a reunião. "
            "Um participante pode ter nenhuma ou várias tasks. Os participantes devem ser mencionados com 'name (company)'. "
            "'due_date' (prazo) deve ser preenchido com a data no formato DD/MM/YYYY. "
            "Caso 'due_date' não seja identificado, preencha com N/A."
        ),
        examples=[
            {
                "owner": "name",
                "company": "company",
                "task": "Enviar a proposta comercial atualizada",
                "due_date": "data",
            },
        ],
    )
