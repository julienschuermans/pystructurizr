"""C4 model of My Fantastic Solution."""
from pystructurizr.dsl import Workspace

workspace = Workspace()

with workspace.Model(name="model") as model:

    # 1. Define the model
    customer = model.Person("Rich Customer")

    with model.SoftwareSystem("Fantastic Web App") as webapp:
        with webapp.Container("Smooth UI", technology='React') as frontend:
            document_renderer = frontend.Component("Document Renderer",)
            backend_client = frontend.Component("Backend Client")
        with webapp.Container("Overengineered API", technology='Connexion') as backend:
            db_client = backend.Component("Database Client")

    with model.SoftwareSystem("Legacy Systems", tags=["external"]) as legacy:
        db = legacy.Container("Slow Database", tags=["database", "external"])

    # 2. Define the relationships
    customer.uses(frontend, "Uses")
    backend_client.uses(backend, "Sends requests to")
    db_client.uses(db, "Reads from and writes to", "JDBC/HTTPS")

# 3. Optional: configure workspace styling
workspace.Styles(
    {"tag": "external", "background": "#807f7e", "color": "#ffffff", },
)
