import logging
import os
import random
import re
import shutil
import uuid
from abc import ABCMeta
from urllib.parse import urljoin

import requests

from great_expectations.data_context.store.store_backend import StoreBackend
from great_expectations.exceptions import InvalidKeyError, StoreBackendError
from great_expectations.util import filter_properties_dict

logger = logging.getLogger(__name__)


class GeCloudStoreBackend(StoreBackend, metaclass=ABCMeta):
    def __init__(
        self,
        ge_cloud_base_url,
        ge_cloud_resource_name,
        ge_cloud_resource_type,
        suppress_store_backend_id=False,
        manually_initialize_store_backend_id: str = "",
        store_name=None,
    ):
        super().__init__(
            fixed_length_key=True,
            suppress_store_backend_id=suppress_store_backend_id,
            manually_initialize_store_backend_id=manually_initialize_store_backend_id,
            store_name=store_name,
        )
        self._ge_cloud_base_url = ge_cloud_base_url
        self._ge_cloud_resource_name = ge_cloud_resource_name
        self._ge_cloud_resource_type = ge_cloud_resource_type

        # Initialize with store_backend_id if not part of an HTMLSiteStore
        if not self._suppress_store_backend_id:
            _ = self.store_backend_id

        # Gather the call arguments of the present function (include the "module_name" and add the "class_name"), filter
        # out the Falsy values, and set the instance "_config" variable equal to the resulting dictionary.
        self._config = {
            "ge_cloud_base_url": ge_cloud_base_url,
            "ge_cloud_resource_name": ge_cloud_resource_name,
            "ge_cloud_resource_type": ge_cloud_resource_type,
            "fixed_length_key": True,
            "suppress_store_backend_id": suppress_store_backend_id,
            "manually_initialize_store_backend_id": manually_initialize_store_backend_id,
            "store_name": store_name,
            "module_name": self.__class__.__module__,
            "class_name": self.__class__.__name__,
        }
        filter_properties_dict(properties=self._config, inplace=True)

    def _get(self, key):
        ge_cloud_url = self.get_url_for_key(key=key)
        headers = {
            "Content-Type": "application/vnd.api+json"
        }
        response = requests.get(ge_cloud_url, headers=headers)
        return response.json()

    def _move(self):
        pass

    def _set(self, key, value, **kwargs):

        data = {
            "data": {
                'type': self.ge_cloud_resource_type,
                "attributes": {
                    "created_by_id": "df665fc4-1891-4ef7-9a12-a0c46015c92c",
                    "checkpoint_config": value.to_json_dict()
                },
            }
        }
        headers = {
            "Content-Type": "application/vnd.api+json"
        }
        url = urljoin(self.ge_cloud_base_url, self.ge_cloud_resource_name)

        try:
            response = requests.post(url, json=data, headers=headers)
            return response.json()
        except Exception as e:
            logger.debug(str(e))
            raise StoreBackendError("Unable to set object in GE Cloud Store Backend.")

    @property
    def ge_cloud_base_url(self):
        return self._ge_cloud_base_url

    @property
    def ge_cloud_resource_name(self):
        return self._ge_cloud_resource_name

    @property
    def ge_cloud_resource_type(self):
        return self._ge_cloud_resource_type

    def list_keys(self):
        pass

    def get_url_for_key(self, key, protocol=None):
        ge_cloud_id = key[0]
        url = urljoin(self.ge_cloud_base_url, f"{self.ge_cloud_resource_name}/{ge_cloud_id}")
        return url

    def remove_key(self, key):
        pass

    def _has_key(self, key):
        all_keys = self.list_keys()
        return key in all_keys

    @property
    def config(self) -> dict:
        return self._config