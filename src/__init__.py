"""
This file registers the model with the Python SDK.
"""

from viam.components.generic import Generic
from viam.resource.registry import Registry, ResourceCreatorRegistration

from .switch import switch

Registry.register_resource_creator(Generic.SUBTYPE, switch.MODEL, ResourceCreatorRegistration(switch.new, switch.validate))
