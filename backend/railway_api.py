"""
Módulo para interactuar con Railway API v2
Clona radiant-ambition para cada cliente, configura variables y despliega
"""
import os
import httpx
from typing import Optional, Dict, Any

RAILWAY_API_URL = "https://backboard.railway.app/graphql/v2"
RAILWAY_ACCESS_TOKEN = os.getenv("RAILWAY_ACCESS_TOKEN", "")
RAILWAY_WORKSPACE_ID = os.getenv("RAILWAY_WORKSPACE_ID", "899e5378-1969-4f91-ad6b-0a3b15f9235e")

TEMPLATE_PROJECT_ID = os.getenv("TEMPLATE_PROJECT_ID", "eaa5e41c-06a2-497b-8696-1417a9f62485")
TEMPLATE_SERVICE_ID = os.getenv("TEMPLATE_SERVICE_ID", "b81e319e-0150-4560-a613-b0f31ec90c4c")
TEMPLATE_ENVIRONMENT_ID = os.getenv("TEMPLATE_ENVIRONMENT_ID", "a9d3cfb8-e212-40fd-8de2-959e06c22497")
TEMPLATE_REPO = os.getenv("TEMPLATE_REPO", "MakerStudios-bot/neurox-instagram-bot")


class RailwayAPI:
    def __init__(self):
        self.url = RAILWAY_API_URL
        self.headers = {
            "Authorization": f"Bearer {RAILWAY_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

    async def _query(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        try:
            payload = {"query": query, "variables": variables or {}}
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.url, json=payload, headers=self.headers)
            data = response.json()
            if "errors" in data:
                error_msg = data["errors"][0]["message"] if data["errors"] else "Unknown error"
                raise Exception(f"Railway API Error: {error_msg}")
            return data.get("data", {})
        except Exception as e:
            print(f"❌ Error en Railway API: {e}")
            raise

    async def obtener_proyectos(self) -> list:
        try:
            query = '{ me { projects { edges { node { id name } } } } }'
            data = await self._query(query)
            proyectos = []
            for edge in data.get("me", {}).get("projects", {}).get("edges", []):
                proyectos.append({"id": edge["node"]["id"], "nombre": edge["node"]["name"]})
            return proyectos
        except Exception as e:
            print(f"Error obteniendo proyectos: {e}")
            return []

    async def obtener_variables_template(self) -> Dict[str, str]:
        """Obtiene las variables del proyecto template radiant-ambition"""
        query = """
        query GetVars($projectId: String!, $environmentId: String!, $serviceId: String!) {
            variables(projectId: $projectId, environmentId: $environmentId, serviceId: $serviceId)
        }
        """
        variables = {
            "projectId": TEMPLATE_PROJECT_ID,
            "environmentId": TEMPLATE_ENVIRONMENT_ID,
            "serviceId": TEMPLATE_SERVICE_ID
        }
        try:
            data = await self._query(query, variables)
            return data.get("variables", {})
        except Exception as e:
            print(f"Error obteniendo variables template: {e}")
            return {}

    async def clonar_proyecto(self, template_nombre: str, nuevo_nombre: str) -> Optional[str]:
        """Clona radiant-ambition creando proyecto nuevo con mismo repo"""
        try:
            # Paso 1: Crear proyecto
            query = """
            mutation ProjectCreate($input: ProjectCreateInput!) {
                projectCreate(input: $input) { id name }
            }
            """
            input_data = {"name": nuevo_nombre}
            if RAILWAY_WORKSPACE_ID:
                input_data["workspaceId"] = RAILWAY_WORKSPACE_ID

            data = await self._query(query, {"input": input_data})
            proyecto_id = data.get("projectCreate", {}).get("id")
            if not proyecto_id:
                return None
            print(f"  ✓ Proyecto creado: {proyecto_id}")

            # Paso 2: Obtener environment ID
            env_query = """
            query GetEnv($id: String!) {
                project(id: $id) { environments { edges { node { id name } } } }
            }
            """
            env_data = await self._query(env_query, {"id": proyecto_id})
            env_edges = env_data.get("project", {}).get("environments", {}).get("edges", [])
            env_id = env_edges[0]["node"]["id"] if env_edges else None

            # Paso 3: Crear servicio con el mismo repo
            svc_query = """
            mutation ServiceCreate($input: ServiceCreateInput!) {
                serviceCreate(input: $input) { id name }
            }
            """
            svc_data = await self._query(svc_query, {
                "input": {
                    "projectId": proyecto_id,
                    "name": f"bot-{nuevo_nombre}",
                    "source": {"repo": TEMPLATE_REPO}
                }
            })
            servicio_id = svc_data.get("serviceCreate", {}).get("id")
            print(f"  ✓ Servicio creado: {servicio_id}")

            # Paso 3.5: Configurar builder y rootDirectory (igual que radiant-ambition)
            if env_id and servicio_id:
                config_query = """
                mutation ConfigService($serviceId: String!, $environmentId: String!, $input: ServiceInstanceUpdateInput!) {
                    serviceInstanceUpdate(serviceId: $serviceId, environmentId: $environmentId, input: $input)
                }
                """
                await self._query(config_query, {
                    "serviceId": servicio_id,
                    "environmentId": env_id,
                    "input": {
                        "builder": "RAILPACK",
                        "rootDirectory": "/vendedor",
                        "startCommand": "",
                        "buildCommand": ""
                    }
                })
                print(f"  ✓ Builder RAILPACK + rootDirectory /vendedor configurado")

            # Paso 4: Copiar variables del template
            template_vars = await self.obtener_variables_template()
            vars_to_copy = {k: v for k, v in template_vars.items() if not k.startswith("RAILWAY_")}

            if vars_to_copy and env_id and servicio_id:
                vars_query = """
                mutation SetVars($input: VariableCollectionUpsertInput!) {
                    variableCollectionUpsert(input: $input)
                }
                """
                await self._query(vars_query, {
                    "input": {
                        "projectId": proyecto_id,
                        "environmentId": env_id,
                        "serviceId": servicio_id,
                        "variables": vars_to_copy
                    }
                })
                print(f"  ✓ Variables copiadas del template")

            # Paso 5: Generar dominio público
            if env_id and servicio_id:
                domain_query = """
                mutation CreateDomain($input: ServiceDomainCreateInput!) {
                    serviceDomainCreate(input: $input) { id domain }
                }
                """
                domain_data = await self._query(domain_query, {
                    "input": {
                        "serviceId": servicio_id,
                        "environmentId": env_id
                    }
                })
                domain = domain_data.get("serviceDomainCreate", {}).get("domain", "")
                print(f"  ✓ Dominio: {domain}")

            # Guardar IDs para configurar variables después
            self._last_env_id = env_id
            self._last_service_id = servicio_id

            return proyecto_id

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
        env_id = getattr(self, '_last_env_id', None)
        service_id = getattr(self, '_last_service_id', None)

        if not env_id or not service_id:
            print(f"  ⚠️ Sin env/service ID para {variable_name}")
            return False

        query = """
        mutation SetVars($input: VariableCollectionUpsertInput!) {
            variableCollectionUpsert(input: $input)
        }
        """
        variables = {
            "input": {
                "projectId": proyecto_id,
                "environmentId": env_id,
                "serviceId": service_id,
                "variables": {variable_name: variable_value}
            }
        }

        try:
            data = await self._query(query, variables)
            return data.get("variableCollectionUpsert", False)
        except Exception as e:
            print(f"Error configurando variable {variable_name}: {e}")
            return False

    async def desplegar_servicio(self, proyecto_id: str) -> bool:
        """El servicio se despliega automáticamente al conectar el repo"""
        print(f"✓ Proyecto {proyecto_id} desplegándose automáticamente")
        return True

    async def obtener_url_servicio(self, proyecto_id: str, servicio_id: str = None) -> Optional[str]:
        query = """
        query GetProject($id: String!) {
            project(id: $id) {
                services { edges { node {
                    serviceInstances { edges { node {
                        domains { serviceDomains { domain } }
                    } } }
                } } }
            }
        }
        """
        try:
            data = await self._query(query, {"id": proyecto_id})
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

    async def obtener_id_proyecto_por_nombre(self, nombre: str) -> Optional[str]:
        try:
            proyectos = await self.obtener_proyectos()
            for p in proyectos:
                if p["nombre"] == nombre:
                    return p["id"]
            return None
        except Exception:
            return None


railway = RailwayAPI()
