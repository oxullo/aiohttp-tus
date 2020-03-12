from pathlib import Path

from aiohttp import web

from . import views
from .annotations import Decorator, Handler
from .constants import APP_TUS_CONFIG_KEY, ROUTE_RESOURCE, ROUTE_UPLOAD
from .data import TusConfig


def setup_tus(
    app: web.Application,
    *,
    upload_path: Path,
    upload_url: str = "/uploads",
    allow_overwrite_files: bool = False,
    decorator: Decorator = None,
) -> web.Application:
    """Setup tus protocol server implementation for aiohttp.web application."""

    def decorate(handler: Handler) -> Handler:
        if decorator is None:
            return handler
        return decorator(handler)

    # Store tus config in application
    app[APP_TUS_CONFIG_KEY] = TusConfig(
        upload_path=upload_path, allow_overwrite_files=allow_overwrite_files,
    )

    # Views for upload management
    app.router.add_options(upload_url, views.upload_options, name=ROUTE_UPLOAD)
    app.router.add_get(upload_url, decorate(views.upload_details))
    app.router.add_post(upload_url, decorate(views.start_upload))

    # Views for resource management
    resource_url = "/".join((upload_url.rstrip("/"), r"{resource_uid}"))
    app.router.add_head(
        resource_url, decorate(views.resource_details), name=ROUTE_RESOURCE
    )
    app.router.add_delete(resource_url, decorate(views.delete_resource))
    app.router.add_patch(resource_url, decorate(views.upload_resource))

    return app
