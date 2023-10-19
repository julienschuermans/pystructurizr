import asyncio
import json
import os
import shutil
import signal
import subprocess
import webbrowser

import click

from .cli_helper import (ensure_tmp_folder_exists, generate_diagram_code_in_child_process, generate_svg)
from .cli_watcher import observe_modules
from .cloudstorage import CloudStorage, create_cloud_storage


@click.command()
@click.option('--view', prompt='Your view file (e.g. examples.single_file_example)',
              help='The view file to generate.')
@click.option('--as-json', is_flag=True, default=False,
              help='Dumps the generated code and the imported modules as a json object')
def dump(view, as_json):
    diagram_code, imported_modules = generate_diagram_code_in_child_process(view)
    if as_json:
        print(json.dumps({
            "code": diagram_code,
            "imported_modules": list(imported_modules)
        }))
    else:
        print(diagram_code)


@click.command()
@click.option('--view', prompt='Your view file (e.g. examples.single_file_example)',
              help='The view file to develop.')
def dev(view):
    click.echo(f"Setting up live preview of view {view}...")
    # Prep the /tmp/pystructurizr folder
    tmp_folder = ensure_tmp_folder_exists()
    current_script_path = os.path.abspath(__file__)
    index_html = os.path.join(os.path.dirname(current_script_path), 'index.html')
    shutil.copy(index_html, f"{tmp_folder}/index.html")

    async def async_behavior():
        print("Generating diagram...")
        diagram_code, imported_modules = generate_diagram_code_in_child_process(view)
        await generate_svg(diagram_code, tmp_folder)
        return imported_modules

    async def observe_loop():
        modules_to_watch = await async_behavior()
        click.echo("Launching webserver...")
        # pylint: disable=consider-using-with
        proc = subprocess.Popen(
            f"httpwatcher --root {tmp_folder} --watch {tmp_folder}",
            shell=True,
            stdout=subprocess.PIPE,
            preexec_fn=os.setsid,
        )
        try:
            await observe_modules(modules_to_watch, async_behavior)
        except:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            raise

    asyncio.run(observe_loop())


@click.command()
@click.option('--view', prompt='Your view file (e.g. examples.single_file_example)',
              help='The view file to render.')
def render(view):
    click.echo("Rendering SVG diagram...")
    diagram_code, _ = generate_diagram_code_in_child_process(view)

    async def _async_behavior():
        # Generate SVG
        await generate_svg(diagram_code, 'output')

    asyncio.run(_async_behavior())
    filename = f'output/{view}.svg'
    shutil.copy('output/diagram.svg', filename)
    print(f"Rendered SVG saved in {filename}")
    # Check if running in WSL
    index = "output/index.html"
    if os.path.exists('/mnt/c/Windows/System32'):
        # Open the file in the default Windows browser
        webbrowser.open_new_tab(index)
    else:
        webbrowser.open_new_tab(f"file://{os.getcwd()}/{index}")


@click.command()
@click.option('--view', prompt='Your view file (e.g. examples.single_file_example)',
              help='The view file to generate and upload to cloud storage.')
@click.option('--gcs-credentials', prompt='Path to json file containing Google Cloud Storage credentials', type=click.Path(exists=True),
              help='Path to the credentials.json file for Google Cloud Storage.')
@click.option('--bucket-name', prompt='Name of the bucket on Google Cloud Storage',
              help='The name of the bucket to use on Google Cloud Storage.')
@click.option('--object-name', prompt='Name of the object on Google Cloud Storage',
              help='The name of the object to use on Google Cloud Storage.')
def build(view, gcs_credentials, bucket_name, object_name):
    async def async_behavior():
        # Generate diagram
        diagram_code, _ = generate_diagram_code_in_child_process(view)
        tmp_folder = ensure_tmp_folder_exists()

        # Generate SVG
        svg_file_path = await generate_svg(diagram_code, tmp_folder)

        # Upload it to the requested cloud storage provider
        cloud_storage = create_cloud_storage(CloudStorage.Provider.GCS, gcs_credentials)
        svg_file_url = cloud_storage.upload_file(svg_file_path, bucket_name, object_name)
        print(svg_file_url)

    asyncio.run(async_behavior())


@click.group()
def cli():
    pass


cli.add_command(dump)
cli.add_command(dev)
cli.add_command(build)
cli.add_command(render)

if __name__ == '__main__':
    cli()
