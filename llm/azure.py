"""Configuração dos modelos Azure OpenAI via LangChain.

Versão standalone de custom/models/azure.py — sem dependência de
custom.settings.llm nem de outros módulos do projeto principal.
"""
from __future__ import annotations

import os
from typing import Optional

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel

from config.settings import (
    AZURE_GPT_LOWCOST_DEPLOYMENT_NAME,
    AZURE_GPT_PREMIUM_DEPLOYMENT_NAME,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_ENDPOINT,
    DEFAULT_LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
)

# Litestar/LangChain workaround: garantir que o endpoint esteja no env
os.environ["AZURE_OPENAI_ENDPOINT"] = AZURE_OPENAI_ENDPOINT


def get_new_gpt4o_model(
    temperature: float = LLM_TEMPERATURE,
    max_tokens: int = DEFAULT_LLM_MAX_TOKENS,
) -> AzureChatOpenAI:
    return AzureChatOpenAI(
        model_name=AZURE_GPT_PREMIUM_DEPLOYMENT_NAME,
        temperature=temperature,
        deployment_name=AZURE_GPT_PREMIUM_DEPLOYMENT_NAME,
        max_tokens=max_tokens,
        openai_api_version=AZURE_OPENAI_API_VERSION,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
    )


def get_new_gptmini_model(
    temperature: float = LLM_TEMPERATURE,
    max_tokens: int = DEFAULT_LLM_MAX_TOKENS,
) -> AzureChatOpenAI:
    return AzureChatOpenAI(
        model_name=AZURE_GPT_LOWCOST_DEPLOYMENT_NAME,
        temperature=temperature,
        deployment_name=AZURE_GPT_LOWCOST_DEPLOYMENT_NAME,
        max_tokens=max_tokens,
        openai_api_version=AZURE_OPENAI_API_VERSION,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
    )


def setup_structured_output_model(
    output_schema: type[BaseModel],
    model_name: str = AZURE_GPT_PREMIUM_DEPLOYMENT_NAME,
    max_tokens: int = DEFAULT_LLM_MAX_TOKENS,
    temperature: float = LLM_TEMPERATURE,
    azure_deployment_name: Optional[str] = AZURE_GPT_PREMIUM_DEPLOYMENT_NAME,
    azure_endpoint: Optional[str] = AZURE_OPENAI_ENDPOINT,
    api_version: Optional[str] = AZURE_OPENAI_API_VERSION,
):
    """Configura modelo com structured output via LangChain."""
    model = AzureChatOpenAI(
        model_name=model_name,
        deployment_name=azure_deployment_name,
        azure_endpoint=azure_endpoint,
        api_version=api_version,
        max_tokens=max_tokens,
        temperature=temperature,
    ).with_config({"run_name": "__ignore"})

    parser = JsonOutputParser(pydantic_object=output_schema)

    prompt = PromptTemplate(
        template="\n{query}\n{format_instructions}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    return prompt | model | parser
