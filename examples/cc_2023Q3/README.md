# Workshop: intro to C4 & (Py)Structurizr

## Goal

The goal of this exercise is to get started with PyStructurizr, a python wrapper around Structurizr DSL.
You can leverage Structurizr DSL to generate C4 diagrams by defining a *Workspace*, one or multiple *Models* and one or multiple *Views*.

## Step by step

### 1. Verify that everything works

1. Setup gcloud

    ```commandline
    gcloud auth login
    gcloud auth application-default login
    gcloud config set project decisive-mapper-401607
    ```

2. Set up virtual environment

    ```commandline
    python3 -m venv --prompt="c4-models" .venv
    source .venv/bin/activate
    pip install -e .
    ```

    <details>
    <summary>In case of problems</summary>
    If you encounter something like:

    <pre>
        ```
        error: invalid command 'bdist_wheel'
        ----------------------------------------
        ERROR: Failed building wheel for pystructurizr
        ```
    </pre>

    You should be able to solve it by running `pip install wheel`
    </details>

3. Create your first diagram

    ```commandline
    cd examples/cc_2023Q3
    pystructurizr render --view systemlandscapeview
    ```

    At this point a browser window should open that renders the System Landscape View of a sample system.

    <details>
    <summary>For more adventurous users</summary>
    You can also use
    <pre>pystructurizr dev --view systemlandscapeview</pre>

    It will also open a browser window that renders your diagram.
    The difference is that the rendered diagram will update automatically as you modify the underlying [workspace.py](./workspace.py). Use `Ctrl-C` to exit.

    However, it will launch a http server in the background which will not
    be stopped appropriately if there is an error in your diagram code.
    You'll have to find the right process ID with `ps aux` and kill it with `kill -9 <PID>`
    </details>

4. To generate a more detailed diagram showing the internals of the **Fantastic Web App**:

    ```commandline
    pystructurizr render --view containerview_webapp
    ```

### 2. Get diagramming

* Have a look at [workspace.py](./workspace.py) to see how the C4 model is built up. Two different views are predefined in [systemlandscapeview.py](./systemlandscapeview.py) and [containerview_webapp.py](./containerview_webapp.py).

* Note that a Software System contains multiple Containers, and a container *can* consist of multiple components. It's easy to draw a diagram thinking about Container level abstractions only - the underlying components can be filled in later!

Modify the diagram into something more interesting. Some ideas:

* Define a new view: a component diagram of the `frontend` container.
* Introduce a new backend Container that relays incoming requests to OpenAI.
* Show how a secondary system leverages the backend API.
* Introduce a new software system that periodically syncs data from the "Slow database" to a new "Fast database".
* Make a C4 diagram of something else entirely.
