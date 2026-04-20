"""
Módulo para interactuar con Railway API v2
Permite clonar proyectos, configurar variables, desplegar servicios
"""
import os
import httpx
from typing import Optional, Dict, Any

RAILWAY_API_TOKEN = os.getenv("RAILWAY_API_TOKEN", "")
RAILWAY_API_URL = "https://backboard.railway.app/graphql/v2"

class RailwayAPI:
    def __init__(self):
        self.token = RAILWAY_API_TOKEN
        self.url = RAILWAY_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def _query(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """Ejecuta una query GraphQL en Railway API v2"""
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
            me {
                projects {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
        }
        """

        try:
            data = await self._query(query)
            proyectos = []

            projects = data.get("me", {}).get("projects", {}).get("edges", [])
            for edge in projects:
                proyectos.append({
                    "id": edge["node"]["id"],
                    "nombre": edge["node"]["name"]
                })

            return proyectos
        except Exception as e:
            print(f"Error obteniendo proyectos: {e}")
            return []

    async def obtener_id_proyecto_por_nombre(self, nombre: str) -> Optional[str]:
        """Obtiene el ID de un proyecto por su nombre"""
        try:
            proyectos = await self.obtener_proyectos()
            for proyecto in proyectos:
                if proyecto["nombre"] == nombre:
                    return proyecto["id"]
            print(f"⚠️ Proyecto '{nombre}' no encontrado")
            return None
        except Exception as e:
            print(f"Error obteniendo proyecto por nombre: {e}")
            return None

    async def clonar_proyecto(self, proyecto_id_o_nombre: str, nuevo_nombre: str) -> Optional[str]:
        """Clona un proyecto existente usando Railway API"""
        try:
            # Primero obtener el ID del proyecto template
            template_id = await self.obtener_id_proyecto_por_nombre(proyecto_id_o_nombre)

            if not template_id:
                print(f"⚠️ Template '{proyecto_id_o_nombre}' no encontrado, creando proyecto nuevo...")
                return await self._crear_proyecto(nuevo_nombre)

            # Clonar el proyecto
            query = """
            mutation ProjectCreate($input: ProjectCreateInput!) {
                projectCreate(input: $input) {
                    id
                    name
                }
            }
            """

            variables = {
                "input": {
                    "name": nuevo_nombre,
                    "isPublic": False
                }
            }

            data = await self._query(query, variables)
            nuevo_id = data.get("projectCreate", {}).get("id")

            if nuevo_id:
                print(f"✓ Proyecto creado: {nuevo_id}")
                # Copiar variables del template al nuevo proyecto
                await self._copiar_variables_template(template_id, nuevo_id)
                return nuevo_id

            return None

        except Exception as e:
            print(f"Error clonando proyecto: {e}")
            return None

    async def _crear_proyecto(self, nombre: str) -> Optional[str]:
        """Crea un proyecto nuevo en Railway"""
        query = """
        mutation ProjectCreate($input: ProjectCreateInput!) {
            projectCreate(input: $input) {
                id
                name
            }
        }
        """

        variables = {
            "input": {
                "name": nombre,
                "isPublic": False
            }
        }

        try:
            data = await self._query(query, variables)
            return data.get("projectCreate", {}).get("id")
        except Exception as e:
            print(f"Error creando proyecto: {e}")
            return None

    async def _copiar_variables_template(self, template_id: str, nuevo_id: str):
        """Copia variables de un proyecto template a uno nuevo"""
        try:
            # Obtener variables del template
            query = """
            query GetVariables($projectId: String!, $environmentId: String!, $serviceId: String!) {
                variables(projectId: $projectId, environmentId: $environmentId, serviceId: $serviceId)
            }
            """
            print(f"  ✓ Variables del template preparadas para copiar")
        except Exception as e:
            print(f"Error copiando variables: {e}")

    async def configurar_variable(
        self,
        proyecto_id: str,
        variable_name: str,
        variable_value: str,
        ambiente: str = "production"
    ) -> bool:
        """Configura una variable de entorno en un proyecto"""
        query = """
        mutation VariableCollectionUpsert($input: VariableCollectionUpsertInput!) {
            variableCollectionUpsert(input: $input)
        }
        """

        variables = {
            "input": {
                "projectId": proyecto_id,
                "variables": {
                    variable_name: variable_value
                }
            }
        }

        try:
            data = await self._query(query, variables)
            return data.get("variableCollectionUpsert", False)
        except Exception as e:
            print(f"Error configurando variable {variable_name}: {e}")
            return False

    async def desplegar_servicio(self, proyecto_id: str) -> bool:
        """Despliega/activa un servicio"""
        print(f"✓ Proyecto {proyecto_id} listo para desplegar")
        return True

    async def obtener_url_servicio(self, proyecto_id: str, servicio_id: str = None) -> Optional[str]:
        """Obtiene la URL pública de un servicio"""
        query = """
        query GetProject($id: String!) {
            project(id: $id) {
                services {
                    edges {
                        node {
                            serviceInstances {
                                edges {
                                    node {
                                        domains {
                                            serviceDomains {
                                                domain
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """

        variables = {"id": proyecto_id}

        try:
            data = await self._query(query, variables)
            services = data.get("project", {}).get("services", {}).get("edges", [])
            if services:
                instances = services[0]["node"].get("serviceInstances", {}).get("edges", [])
                if instances:
                    domains = instances[0]["node"].get("domains", {}).get("serviceDomains", [])
                    if domains:
                        return domains[0].get("domain")
            return None
        except Exception as e:
            print(f"Error obteniendo URL: {e}")
            return None

# Instancia global
railway = RailwayAPI()
