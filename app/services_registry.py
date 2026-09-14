"""Dynamic allowlist of Google Ads services and methods from the installed client."""

from __future__ import annotations

import importlib
import os
import pkgutil
import re
from functools import lru_cache
from typing import Any

from google.ads.googleads.client import _DEFAULT_VERSION
import google.ads.googleads as googleads_root


def _service_module_name(service_name: str) -> str:
    if not service_name.endswith("Service"):
        raise ValueError("service_name must end with 'Service' (e.g. CampaignService).")
    snake = re.sub(r"(?<!^)(?=[A-Z])", "_", service_name).lower()
    return snake


@lru_cache(maxsize=1)
def discover_services() -> dict[str, list[str]]:
    root = os.path.dirname(googleads_root.__file__)
    services_dir = os.path.join(root, _DEFAULT_VERSION, "services", "services")
    allowlist: dict[str, list[str]] = {}
    for mod in pkgutil.iter_modules([services_dir]):
        if not mod.name.endswith("_service"):
            continue
        module = importlib.import_module(
            f"google.ads.googleads.{_DEFAULT_VERSION}.services.services.{mod.name}"
        )
        pascal = "".join(part.capitalize() for part in mod.name.split("_"))
        client_cls_name = f"{pascal}Client"
        if not hasattr(module, client_cls_name):
            continue
        client_cls = getattr(module, client_cls_name)
        methods = [
            name
            for name in dir(client_cls)
            if not name.startswith("_")
            and callable(getattr(client_cls, name))
            and name not in {"close", "transport", "api_endpoint"}
        ]
        service_name = pascal.replace("_", "")
        if service_name.endswith("Service"):
            allowlist[service_name] = sorted(methods)
    return allowlist


def validate_service_call(service_name: str, method_name: str) -> None:
    services = discover_services()
    if service_name not in services:
        raise ValueError(
            f"Unknown service '{service_name}'. Must be one of the installed Google Ads services."
        )
    if method_name not in services[service_name]:
        raise ValueError(
            f"Method '{method_name}' is not available on {service_name}."
        )


def discover_mutate_methods() -> dict[str, str]:
    """Map service name -> primary mutate_* method name."""
    services = discover_services()
    mapping: dict[str, str] = {}
    for service, methods in services.items():
        mutate_methods = [m for m in methods if m.startswith("mutate_")]
        if mutate_methods:
            mapping[service] = mutate_methods[0]
    return mapping


def resource_type_to_service(resource_type: str) -> str:
    if not resource_type:
        raise ValueError("resource_type is required.")
    if resource_type.endswith("Service"):
        return resource_type
    return f"{resource_type}Service"


def operation_type_for_resource(resource_type: str, op: str) -> str:
    op = op.lower()
    if op not in {"create", "update", "remove"}:
        raise ValueError("operation_type must be create, update, or remove.")
    return op


def build_operation_message_name(resource_type: str) -> str:
    return f"{resource_type}Operation"
