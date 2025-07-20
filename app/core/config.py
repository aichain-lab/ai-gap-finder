"""Configuration management for AI Gap Finder"""

import os
import yaml
from typing import List, Optional
from pydantic import BaseSettings, Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    app_name: str = "AI Gap Finder"
    version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = True
    log_level: str = "INFO"
    
    # OpenAI settings
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 2000
    openai_timeout: int = 30
    
    # PDF settings
    pdf_max_file_size: int = 10485760  # 10MB
    pdf_allowed_extensions: List[str] = [".pdf"]
    
    # Embedding settings
    embedding_model: str = "text-embedding-ada-002"
    embedding_chunk_size: int = 1000
    embedding_chunk_overlap: int = 200
    
    # ArXiv settings
    arxiv_base_url: str = "http://export.arxiv.org/api/query"
    arxiv_max_results: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def load_config_from_yaml(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file"""
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    return {}


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)"""
    # Load from YAML first
    yaml_config = load_config_from_yaml()
    
    # Flatten the nested YAML structure
    flat_config = {}
    if yaml_config:
        app_config = yaml_config.get('app', {})
        llm_config = yaml_config.get('llm', {})
        pdf_config = yaml_config.get('pdf', {})
        embedding_config = yaml_config.get('embedding', {})
        arxiv_config = yaml_config.get('arxiv', {})
        logging_config = yaml_config.get('logging', {})
        
        # Map YAML keys to Settings attributes
        flat_config.update({
            'app_name': app_config.get('name'),
            'version': app_config.get('version'),
            'host': app_config.get('host'),
            'port': app_config.get('port'),
            'debug': app_config.get('debug'),
            'openai_model': llm_config.get('model'),
            'openai_temperature': llm_config.get('temperature'),
            'openai_max_tokens': llm_config.get('max_tokens'),
            'openai_timeout': llm_config.get('timeout'),
            'pdf_max_file_size': pdf_config.get('max_file_size'),
            'pdf_allowed_extensions': pdf_config.get('allowed_extensions'),
            'embedding_model': embedding_config.get('model'),
            'embedding_chunk_size': embedding_config.get('chunk_size'),
            'embedding_chunk_overlap': embedding_config.get('chunk_overlap'),
            'arxiv_base_url': arxiv_config.get('base_url'),
            'arxiv_max_results': arxiv_config.get('max_results'),
            'log_level': logging_config.get('level'),
        })
        
        # Remove None values
        flat_config = {k: v for k, v in flat_config.items() if v is not None}
    
    return Settings(**flat_config)
