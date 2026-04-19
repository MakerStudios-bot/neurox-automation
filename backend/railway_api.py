"""
Módulo para interactuar con Railway API
Permite clonar proyectos, configurar variables, desplegar servicios
"""
import os
import httpx
import json
from typing import Optional, Dict, Any

RAILWAY_API_TOKEN = os.getenv("RAILWAY_API_TOKEN", "")
RAILWAY_API_URL = os.getenv("RAILWAY_API_URL", "https://api.railway.app/graphql")

class RailwayAPI:
    def __init__(self):
        self.token = RAILWAY_API_TOKEN
        self.url = RAILWAY_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def _query(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """Ejecuta una query GraphQL en Railway API"""
        try:
            payload = {
                "query": query,
                "variables": variables or {}
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.url,
                    json=payload,
                    headers=self.headers
                )

            data = response.json()

            if "errors" in data:
                error_msg = data["errors"][0]["message"] if data["errors"] else "Unknown error"
                raise Exception(f"Railway API Error: {error_msg}")

            return data.get("data", {})

        except Exception as e:
            print(f"❌ Error en Railway API: {e}")
            raise

    async def obtener_proyectos(self) -> list:
        """Obtiene lista de proyectos disponibles"""
        query = """
        query {
            projects(first: 100) {
                edges {
                    node {
                        id
                        name
                    }
                }
            }
        }
        """

        try:
            data = await self._query(query)
            proyectos = []

            if "projects" in data and "edges" in data["projects"]:
                for edge in data["projects"]["edges"]:
                    proyectos.append({
                        "id": edge["node"]["id"],
                        "nombre": edge["node"]["name"]
                    })

            return proyectos
        except Exception as e:
            print(f"Error obteniendo proyectos: {e}")
            return []

    async def clonar_proyecto(self, proyecto_id: str, nuevo_nombre: str) -> Optional[str]:
        """Clona un proyecto existente"""
        query = """
        mutation CloneProject($projectId: String!, $name: String!) {
            projectClone(input: {
                projectId: $projectId
                name: $name
            }) {
                project {
                    id
                    name
                }
            }
        }
        """

        variables = {
            "projectId": proyecto_id,
            "name": nuevo_nombre
        }

        try:
            data = await self._query(query, variables)

            if "projectClone" in data and "project" in data["projectClone"]:
                return data["projectClone"]["project"]["id"]

            return None
        except Exception as e:
            print(f"Error clonando proyecto: {e}")
            return None

    async def configurar_variable(
        self,
        proyecto_id: str,
        variable_name: str,
        variable_value: str,
        ambiente: str = "production"
    ) -> bool:
        """Configura una variable de entorno en un proyecto"""
        query = """
        mutation UpsertVariable($projectId: String!, $environmentId: String, $name: String!, $value: String!) {
            variableUpsert(input: {
                projectId: $projectId
                environmentId: $environmentId
                name: $name
                value: $value
            }) {
                variable {
                    id
                    name
                }
            }
        }
        """

        variables = {
            "projectId": proyecto_id,
            "environmentId": None,
            "name": variable_name,
            "value": variable_value
        }

        try:
            data = await self._query(query, variables)
            return "variableUpsert" in data
        except Exception as e:
            print(f"Error configurando variable {variable_name}: {e}")
            return False

    async def desplegar_servicio(self, proyecto_id: str) -> bool:
        """Despliega/activa un servicio"""
        # Railway deploya automáticamente cuando se pushea código
        # Esta función es placeholder para futura lógica
        print(f"✓ Proyecto {proyecto_id} listo para desplegar")
        return True

    async def obtener_url_servicio(self, proyecto_id: str, servicio_id: str) -> Optional[str]:
        """Obtiene la URL pública de un servicio"""
        query = """
        query GetService($projectId: String!, $serviceId: String!) {
            service(projectId: $projectId, id: $serviceId) {
                id
                deployments(first: 1) {
                    edges {
                        node {
                            url
                        }
                    }
                }
            }
        }
        """

        variables = {
            "projectId": proyecto_id,
            "serviceId": servicio_id
        }

        try:
            data = await self._query(query, variables)

            if "service" in data and "deployments" in data["service"]:
                edges = data["service"]["deployments"].get("edges", [])
                if edges and len(edges) > 0:
                    return edges[0]["node"].get("url")

            return None
        except Exception as e:
            print(f"Error obteniendo URL: {e}")
            return None

# Instancia global
railway = RailwayAPI()
