"""App commands for the Reflex Cloud CLI."""

from __future__ import annotations

import json

import click
from tabulate import tabulate

from reflex_cli import constants
from reflex_cli.core.config import Config
from reflex_cli.utils import console
from reflex_cli.utils.exceptions import (
    ConfigInvalidFieldValueError,
    NotAuthenticatedError,
    ResponseError,
    ScaleAppError,
    ScaleParamError,
    ScaleTypeError,
)


@click.group()
def apps_cli():
    """Commands for managing apps."""
    pass


@apps_cli.command(name="history")
@click.argument("app_id", required=False)
@click.option("--app-name", help="The name of the application.")
@click.option("--token", help="The authentication token.")
@click.option(
    "--loglevel",
    type=click.Choice([level.value for level in constants.LogLevel]),
    default=constants.LogLevel.INFO.value,
    help="The log level to use.",
)
@click.option(
    "-j",
    "--json",
    "as_json",
    is_flag=True,
    help="Whether to output the result in json format.",
)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    default=True,
    help="Whether to use interactive mode.",
)
def app_history(
    app_id: str | None,
    app_name: str | None,
    token: str | None,
    loglevel: str,
    as_json: bool,
    interactive: bool,
):
    """Retrieve the deployment history for a given application."""
    from reflex_cli.utils import hosting

    console.set_log_level(loglevel)
    try:
        authenticated_client = hosting.get_authenticated_client(
            token=token, interactive=interactive
        )
        if app_name is not None and app_id is None:
            result = hosting.search_app(
                app_name=app_name,
                project_id=None,
                client=authenticated_client,
                interactive=interactive,
            )
            app_id = result.get("id") if result else None

        if not app_id:
            console.error("No valid app_id or app_name provided.")
            raise click.exceptions.Exit(1)

        history = hosting.get_app_history(app_id=app_id, client=authenticated_client)

        if as_json:
            console.print(json.dumps(history))
            return
        if history:
            headers = list(history[0].keys())
            table = [list(deployment.values()) for deployment in history]
            console.print(tabulate(table, headers=headers))
        else:
            console.print(str(history))
    except NotAuthenticatedError as err:
        console.error("You are not authenticated. Run `reflex login` to authenticate.")
        raise click.exceptions.Exit(1) from err


@apps_cli.command("build-logs")
@click.argument("deployment_id", required=True)
@click.option("--token", help="The authentication token.")
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    default=True,
    help="Whether to use interactive mode.",
)
def deployment_build_logs(
    deployment_id: str,
    token: str | None,
    interactive: bool,
):
    """Retrieve the build logs for a specific deployment."""
    from reflex_cli.utils import hosting

    try:
        authenticated_client = hosting.get_authenticated_client(
            token=token, interactive=interactive
        )
        logs = hosting.get_deployment_build_logs(
            deployment_id=deployment_id, client=authenticated_client
        )
        console.print(logs)
    except NotAuthenticatedError as err:
        console.error("You are not authenticated. Run `reflex login` to authenticate.")
        raise click.exceptions.Exit(1) from err


@apps_cli.command(name="status")
@click.argument("deployment_id", required=True)
@click.option("--watch", is_flag=True, help="Whether to continuously watch the status.")
@click.option("--token", help="The authentication token.")
@click.option(
    "--loglevel",
    type=click.Choice([level.value for level in constants.LogLevel]),
    default=constants.LogLevel.INFO.value,
    help="The log level to use.",
)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    default=True,
    help="Whether to use interactive mode.",
)
def deployment_status(
    deployment_id: str,
    watch: bool,
    token: str | None,
    loglevel: str,
    interactive: bool,
):
    """Retrieve the status of a specific deployment."""
    from reflex_cli.utils import hosting

    console.set_log_level(loglevel)

    try:
        authenticated_client = hosting.get_authenticated_client(
            token=token, interactive=interactive
        )
        if watch:
            status = hosting.watch_deployment_status(
                deployment_id=deployment_id, client=authenticated_client
            )
            if status is False:
                raise click.exceptions.Exit(1)
        else:
            status = hosting.get_deployment_status(
                deployment_id=deployment_id, client=authenticated_client
            )
            console.error(status) if "failed" in status else console.print(status)
    except NotAuthenticatedError as err:
        console.error("You are not authenticated. Run `reflex login` to authenticate.")
        raise click.exceptions.Exit(1) from err


@apps_cli.command(name="stop")
@click.argument("app_id", required=False)
@click.option("--app-name", help="The name of the application.")
@click.option("--token", help="The authentication token.")
@click.option(
    "--loglevel",
    type=click.Choice([level.value for level in constants.LogLevel]),
    default=constants.LogLevel.INFO.value,
    help="The log level to use.",
)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    default=True,
    help="Whether to use interactive mode.",
)
def stop_app(
    app_id: str | None,
    app_name: str | None,
    token: str | None,
    loglevel: str,
    interactive: bool,
):
    """Stop a running application."""
    from reflex_cli.utils import hosting

    console.set_log_level(loglevel)

    try:
        authenticated_client = hosting.get_authenticated_client(
            token=token, interactive=interactive
        )
        if app_name is not None and app_id is None:
            app_result = hosting.search_app(
                app_name=app_name,
                project_id=None,
                client=authenticated_client,
                interactive=interactive,
            )
            app_id = app_result.get("id") if app_result else None

        if not app_id:
            console.error("No valid app_id or app_name provided.")
            raise click.exceptions.Exit(1)

        result = hosting.stop_app(app_id=app_id, client=authenticated_client)
        if result:
            console.error(result) if "failed" in result else console.success(result)
    except NotAuthenticatedError as err:
        console.error("You are not authenticated. Run `reflex login` to authenticate.")
        raise click.exceptions.Exit(1) from err


@apps_cli.command(name="start")
@click.argument("app_id", required=False)
@click.option("--app-name", help="The name of the application.")
@click.option("--token", help="The authentication token.")
@click.option(
    "--loglevel",
    type=click.Choice([level.value for level in constants.LogLevel]),
    default=constants.LogLevel.INFO.value,
    help="The log level to use.",
)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    default=True,
    help="Whether to use interactive mode.",
)
def start_app(
    app_id: str | None,
    app_name: str | None,
    token: str | None,
    loglevel: str,
    interactive: bool,
):
    """Start a stopped application."""
    from reflex_cli.utils import hosting

    console.set_log_level(loglevel)
    try:
        authenticated_client = hosting.get_authenticated_client(
            token=token, interactive=interactive
        )
        if app_name is not None and app_id is None:
            app_result = hosting.search_app(
                app_name=app_name,
                project_id=None,
                client=authenticated_client,
                interactive=interactive,
            )
            app_id = app_result.get("id") if app_result else None

        if not app_id:
            console.error("No valid app_id or app_name provided.")
            raise click.exceptions.Exit(1)

        result = hosting.start_app(app_id=app_id, client=authenticated_client)
        if result:
            console.error(result) if "failed" in result else console.success(result)
    except NotAuthenticatedError as err:
        console.error("You are not authenticated. Run `reflex login` to authenticate.")
        raise click.exceptions.Exit(1) from err


@apps_cli.command(name="delete")
@click.argument("app_id", required=False)
@click.option("--app-name", help="The name of the application.")
@click.option("--token", help="The authentication token.")
@click.option(
    "--loglevel",
    type=click.Choice([level.value for level in constants.LogLevel]),
    default=constants.LogLevel.INFO.value,
    help="The log level to use.",
)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    default=True,
    help="Whether to use interactive mode.",
)
def delete_app(
    app_id: str | None,
    app_name: str | None,
    token: str | None,
    loglevel: str,
    interactive: bool,
):
    """Delete an application."""
    from reflex_cli.utils import hosting

    console.set_log_level(loglevel)
    try:
        authenticated_client = hosting.get_authenticated_client(
            token=token, interactive=interactive
        )
        if app_name is not None and app_id is None:
            app_result = hosting.search_app(
                app_name=app_name,
                project_id=None,
                client=authenticated_client,
                interactive=interactive,
            )
            app_id = app_result.get("id") if app_result else None

        if not app_id:
            console.error("No valid app_id or app_name provided.")
            raise click.exceptions.Exit(1)

        result = hosting.delete_app(app_id=app_id, client=authenticated_client)
        if result:
            console.warn(result)
    except NotAuthenticatedError as err:
        console.error("You are not authenticated. Run `reflex login` to authenticate.")
        raise click.exceptions.Exit(1) from err


@apps_cli.command(name="logs")
@click.argument("app_id", required=False)
@click.option("--app-name", help="The name of the application.")
@click.option("--token", help="The authentication token.")
@click.option("--offset", type=int, help="The offset in seconds from the current time.")
@click.option("--start", type=int, help="The start time in Unix epoch format.")
@click.option("--end", type=int, help="The end time in Unix epoch format.")
@click.option(
    "--loglevel",
    type=click.Choice([level.value for level in constants.LogLevel]),
    default=constants.LogLevel.INFO.value,
    help="The log level to use.",
)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    default=True,
    help="Whether to use interactive mode.",
)
def app_logs(
    app_id: str | None,
    app_name: str | None,
    token: str | None,
    offset: int | None,
    start: int | None,
    end: int | None,
    loglevel: str,
    interactive: bool,
):
    """Retrieve logs for a given application."""
    from reflex_cli.utils import hosting

    authenticated_client = hosting.get_authenticated_client(
        token=token, interactive=interactive
    )
    if app_name is not None and app_id is None:
        app_result = hosting.search_app(
            app_name=app_name,
            project_id=None,
            client=authenticated_client,
            interactive=interactive,
        )
        app_id = app_result.get("id") if app_result else None

    if not app_id:
        console.error("No valid app_id or app_name provided.")
        raise click.exceptions.Exit(1)

    if offset is None and start is None and end is None:
        offset = 3600
    if (offset is not None and start) or end:
        console.error("must provide both start and end")
        raise click.exceptions.Exit(1)

    console.set_log_level(loglevel)

    try:
        result = hosting.get_app_logs(
            app_id=app_id,
            offset=offset,
            start=start,
            end=end,
            client=authenticated_client,
        )
        if result:
            if isinstance(result, list):
                result.reverse()
                for log in result:
                    console.warn(log)
            else:
                console.warn("Unable to retrieve logs.")
    except NotAuthenticatedError as err:
        console.error("You are not authenticated. Run `reflex login` to authenticate.")
        raise click.exceptions.Exit(1) from err


@apps_cli.command(name="list")
@click.option("--project", "project_id", help="The project ID to filter deployments.")
@click.option("--project-name", help="The name of the project.")
@click.option("--token", help="The authentication token.")
@click.option(
    "--loglevel",
    type=click.Choice([level.value for level in constants.LogLevel]),
    default=constants.LogLevel.INFO.value,
    help="The log level to use.",
)
@click.option(
    "-j",
    "--json",
    "as_json",
    is_flag=True,
    help="Whether to output the result in JSON format.",
)
@click.option(
    "--interactive",
    is_flag=True,
    default=True,
    help="Whether to list configuration options and ask for confirmation.",
)
def list_apps(
    project_id: str | None,
    project_name: str | None,
    token: str | None,
    loglevel: str,
    as_json: bool,
    interactive: bool,
):
    """List all the hosted deployments of the authenticated user. Will exit if unable to list deployments."""
    from reflex_cli.utils import hosting

    console.set_log_level(loglevel)

    authenticated_client = hosting.get_authenticated_client(
        token=token, interactive=interactive
    )

    if project_name and not project_id:
        result = hosting.search_project(
            project_name, client=authenticated_client, interactive=interactive
        )
        project_id = result.get("id") if result else None

    if project_id is None:
        project_id = hosting.get_selected_project()
    try:
        deployments = hosting.list_apps(project=project_id, client=authenticated_client)
    except Exception as ex:
        console.error("Unable to list deployments")
        raise click.exceptions.Exit(1) from ex

    if as_json:
        console.print(json.dumps(deployments))
        return
    if deployments:
        headers = list(deployments[0].keys())
        table = [list(deployment.values()) for deployment in deployments]
        console.print(tabulate(table, headers=headers))
    else:
        console.print(str(deployments))


@apps_cli.command(name="scale")
@click.argument("app_id", required=False)
@click.option("--app-name", help="The name of the app.")
@click.option("--vm-type", help="The virtual machine type to scale to.")
@click.option("--regions", "-r", multiple=True, help="Region to scale the app to.")
@click.option("--token", help="The authentication token.")
@click.option(
    "--loglevel",
    type=click.Choice([level.value for level in constants.LogLevel]),
    default=constants.LogLevel.INFO.value,
    help="The log level to use.",
)
@click.option("--scale-type", help="The type of scaling.")
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    default=True,
    help="Whether to use interactive mode.",
)
def scale_app(
    app_id: str | None,
    app_name: str | None,
    vm_type: str | None,
    regions: tuple[str, ...],
    token: str | None,
    loglevel: str,
    scale_type: str | None,
    interactive: bool,
):
    """Scale an application by changing the VM type or adding/removing regions."""
    from reflex_cli.utils import hosting

    console.set_log_level(loglevel)
    try:
        authenticated_client = hosting.get_authenticated_client(
            token=token, interactive=interactive
        )

        cli_args = hosting.ScaleAppCliArgs.create(
            regions=list(regions), vm_type=vm_type, scale_type=scale_type
        )
        config = Config.from_yaml_or_default().with_overrides(
            vmtype=cli_args.vm_type,
            regions=cli_args.regions,
        )

        if not config.exists() and not cli_args.is_valid:
            console.error(
                "specify either --vm-type or --regions or add them to the cloud.yml file"
            )
            raise click.exceptions.Exit(1)

        if config.exists() and cli_args.is_valid:
            console.warn(
                "CLI arguments will override the values in the cloud.yml file."
            )
        scale_params = hosting.ScaleParams.from_config(config).set_type_from_cli_args(
            cli_args
        )

        # If app_name is provided, find the app_id
        if app_name is not None and app_id is None:
            app_result = hosting.search_app(
                app_name=app_name,
                project_id=None,
                client=authenticated_client,
                interactive=interactive,
            )
            app_id = app_result.get("id") if app_result else None

        if not app_id:
            console.error("No valid app_id or app_name provided.")
            raise click.exceptions.Exit(1)

        hosting.scale_app(
            app_id=app_id, scale_params=scale_params, client=authenticated_client
        )
        console.success("Successfully scaled the app.")

    except NotAuthenticatedError as err:
        console.error("You are not authenticated. Run `reflex login` to authenticate.")
        raise click.exceptions.Exit(1) from err
    except (
        ScaleAppError,
        ResponseError,
        ConfigInvalidFieldValueError,
        ScaleTypeError,
        ScaleParamError,
    ) as err:
        console.error(err.args[0])
        raise click.exceptions.Exit(1) from err
