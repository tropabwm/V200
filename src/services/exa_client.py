#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Exa Client
Cliente para integração com Exa API para pesquisa avançada
"""

import os
import logging
import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from exa_py import Exa

logger = logging.getLogger(__name__)

class ExaClient:
    """Cliente para integração com Exa API"""

    def __init__(self):
        """Inicializa cliente Exa"""
        self.api_key = os.getenv("EXA_API_KEY", "a0dd63a6-0bd1-488f-a63e-2c4f4cfe969f")
        self.base_url = "https://api.exa.ai"

        if self.api_key:
            try:
                self.client = Exa(self.api_key)
                logger.info("✅ Exa client inicializado com sucesso")
                self.available = True
            except Exception as e:
                logger.error(f"⚠️ Erro ao inicializar Exa client: {e}")
                self.available = False
                self.client = None
        else:
            logger.warning("⚠️ Exa API key não encontrada")
            self.available = False
            self.client = None


    def is_available(self) -> bool:
        """Verifica se o cliente está disponível"""
        return self.available

    def search(
        self,
        query: str,
        num_results: int = 10,
        include_domains: List[str] = None,
        exclude_domains: List[str] = None,
        start_crawl_date: str = None,
        end_crawl_date: str = None,
        start_published_date: str = None,
        end_published_date: str = None,
        use_autoprompt: bool = True,
        type: str = "neural"
    ) -> Optional[Dict[str, Any]]:
        """Realiza busca usando Exa API"""

        if not self.available:
            logger.warning("Exa não está disponível")
            return None

        try:
            payload = {
                "query": query,
                "numResults": num_results,
                "useAutoprompt": use_autoprompt,
                "type": type
            }

            if include_domains:
                payload["includeDomains"] = include_domains

            if exclude_domains:
                payload["excludeDomains"] = exclude_domains

            if start_crawl_date:
                payload["startCrawlDate"] = start_crawl_date

            if end_crawl_date:
                payload["endCrawlDate"] = end_crawl_date

            if start_published_date:
                payload["startPublishedDate"] = start_published_date

            if end_published_date:
                payload["endPublishedDate"] = end_published_date

            response = self.client.search(**payload)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Exa search: {len(data.get('results', []))} resultados")
                return data
            else:
                logger.error(f"❌ Erro Exa: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"❌ Erro na requisição Exa: {str(e)}")
            return None

    def get_contents(
        self,
        ids: List[str],
        text: bool = True,
        highlights: bool = False,
        summary: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Obtém conteúdo detalhado dos resultados"""

        if not self.available:
            return None

        try:
            payload = {
                "ids": ids,
                "text": text,
                "highlights": highlights,
                "summary": summary
            }

            response = self.client.get_contents(**payload)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Exa contents: {len(data.get('results', []))} conteúdos")
                return data
            else:
                logger.error(f"❌ Erro Exa contents: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"❌ Erro ao obter conteúdos Exa: {str(e)}")
            return None

    def find_similar(
        self,
        url: str,
        num_results: int = 10,
        exclude_source_domain: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Encontra páginas similares"""

        if not self.available:
            return None

        try:
            payload = {
                "url": url,
                "numResults": num_results,
                "excludeSourceDomain": exclude_source_domain
            }

            response = self.client.find_similar(**payload)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Exa similar: {len(data.get('results', []))} similares")
                return data
            else:
                logger.error(f"❌ Erro Exa similar: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"❌ Erro ao buscar similares: {str(e)}")
            return None

    def search_comprehensive(self, query: str, num_results: int = 10, **kwargs) -> Dict[str, Any]:
        """Busca abrangente com múltiplas estratégias e filtros avançados"""
        try:
            if not self.api_key:
                logger.warning("Exa API key não configurada")
                return {
                    'success': False,
                    'error': 'API key não configurada',
                    'query': query,
                    'results': []
                }

            # Configurações avançadas para busca comprehensive
            search_params = {
                'query': query,
                'num_results': min(num_results, 20),  # Limite máximo
                'use_autoprompt': True,
                'type': 'neural',
                'include_domains': kwargs.get('include_domains', []),
                'exclude_domains': kwargs.get('exclude_domains', []),
                'start_crawl_date': kwargs.get('start_date'),
                'end_crawl_date': kwargs.get('end_date'),
                'include_text': True,
                'text_length_min': kwargs.get('min_length', 200),
                'text_length_max': kwargs.get('max_length', 2000)
            }

            # Remove parâmetros None
            search_params = {k: v for k, v in search_params.items() if v is not None}

            logger.info(f"🔍 Iniciando busca comprehensive Exa: {query}")

            # Realiza busca neural
            try:
                response = self.client.search_and_contents(**search_params)

                processed_results = []
                if hasattr(response, 'results') and response.results:
                    for result in response.results:
                        processed_result = {
                            'title': getattr(result, 'title', 'Sem título'),
                            'url': getattr(result, 'url', ''),
                            'text': getattr(result, 'text', '')[:2000],  # Limita texto
                            'score': getattr(result, 'score', 0),
                            'published_date': getattr(result, 'published_date', None),
                            'author': getattr(result, 'author', None),
                            'source': 'exa_neural',
                            'relevance_score': getattr(result, 'score', 0) * 100
                        }

                        # Filtra resultados com conteúdo mínimo
                        if len(processed_result['text'].strip()) >= 100:
                            processed_results.append(processed_result)

                logger.info(f"✅ Exa encontrou {len(processed_results)} resultados relevantes")

                return {
                    'success': True,
                    'query': query,
                    'total_results': len(processed_results),
                    'results': processed_results,
                    'search_strategy': 'comprehensive_neural',
                    'timestamp': datetime.now().isoformat(),
                    'search_params': search_params
                }

            except Exception as api_error:
                logger.error(f"Erro na API Exa: {api_error}")

                # Fallback para busca básica
                return self._fallback_basic_search(query, num_results)

        except Exception as e:
            logger.error(f"❌ Erro na busca comprehensive Exa: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query,
                'results': []
            }

    def _fallback_basic_search(self, query: str, num_results: int) -> Dict[str, Any]:
        """Busca básica como fallback"""
        try:
            basic_params = {
                'query': query,
                'num_results': min(num_results, 10),
                'use_autoprompt': True
            }

            response = self.client.search(**basic_params)

            results = []
            if hasattr(response, 'results') and response.results:
                for result in response.results:
                    results.append({
                        'title': getattr(result, 'title', 'Sem título'),
                        'url': getattr(result, 'url', ''),
                        'text': '',  # Busca básica não retorna texto
                        'score': getattr(result, 'score', 0),
                        'source': 'exa_basic'
                    })

            return {
                'success': True,
                'query': query,
                'total_results': len(results),
                'results': results,
                'search_strategy': 'basic_fallback',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Falha no fallback básico Exa: {e}")
            return {
                'success': False,
                'error': f"Busca básica falhou: {str(e)}",
                'query': query,
                'results': []
            }

# Instância global
exa_client = ExaClient()