"""Config helper functions to manage configuration and rebuilt your task pipeline.

Config format: json
(1) include attribute and entity_name to reconstruct all attributes of a pipeline.

Example:
    {  # attribute and its config to recreate the component
        "document_splitter": {
            "entity_name": "DocumentSplitter",
            "entity_config": {
                "split_by": "word",
                "split_length": 400,
                "split_overlap": 200,
            },
        },
        "to_embeddings": {
            "entity_name": "ToEmbeddings",
            "entity_config": {
                "vectorizer": {
                    "entity_name": "Embedder",
                    "entity_config": {
                        "model_client": {
                            "entity_name": "OpenAIClient",
                            "entity_config": {},
                        },
                        "model_kwargs": {
                            "model": "text-embedding-3-small",
                            "dimensions": 256,
                            "encoding_format": "float",
                        },
                    },
                    # the other config is to instantiate the entity (class and function) with the given config as arguments
                    # "entity_state": "storage/embedder.pkl", # this will load back the state of the entity
                },
                "batch_size": 100,
            },
        },
    }


(2) only include the config as arguments and does not include any entity_name or attribute.
You can use this manually to construct an entity yourself.

Example:
{
   "Embedder":   # it can be any name
    {
        "model_client": "OpenAIClient",
        "model_kwargs": {
            "api_key": "your_api_key",
            "model_name": "text-embedder"
        }
    },
    "FAISSRetriever": {
        "top_k": 2,
        "dimensions": 256,
        "vectorizer": "embedder"
    }
}
"""

from typing import Any, Dict
from lightrag.utils.registry import EntityMapping


def construct_component(config: Dict[str, Any]) -> Any:
    __doc__ = (
        r"""Construct an componenet from a configuration dictionary. Format type 1"""
    )

    component_name = config["component_name"]
    component_cls = EntityMapping.get(component_name)
    component_config: Dict = config.get("component_config", {})

    initialized_config = {}

    for key, value in component_config.items():
        if isinstance(value, dict) and "component_name" in value:
            # Recursively construct sub-entities
            initialized_config[key] = construct_component(value)
        else:
            initialized_config[key] = value

    return component_cls(**initialized_config)


def construct_components_from_config(
    config: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    __doc__ = r"""Construct multiple components from a configuration dictionary. Format type 1"""
    components = {}
    for attr, component_config in config.items():
        components[attr] = construct_component(component_config)
    return components