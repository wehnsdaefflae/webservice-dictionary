import json
from collections.abc import MutableMapping
from typing import Iterator, TypeVar, Dict, Any, Tuple, Optional, Union
import requests

"""
import logging

import http.client
http.client.HTTPConnection.debuglevel = 1

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
"""

T = TypeVar('T')  # Any type.
KT = TypeVar('KT')  # Key type.
VT = TypeVar('VT')  # Value type.
T_co = TypeVar('T_co', covariant=True)  # Any type covariant containers.
V_co = TypeVar('V_co', covariant=True)  # Any type covariant containers.
VT_co = TypeVar('VT_co', covariant=True)  # Value type covariant containers.
T_contra = TypeVar('T_contra', contravariant=True)  # Ditto contravariant.

# Internal type variable used for Type[].
CT_co = TypeVar('CT_co', covariant=True, bound=type)


class WSDict(MutableMapping):
    _set = "api/webservice-dictionary/v1/set/"
    _get = "api/webservice-dictionary/v1/get/"
    _pop = "api/webservice-dictionary/v1/pop/"
    _complete = "api/webservice-dictionary/v1/complete/"

    def __init__(self, url_base: str, seq: Optional[Union[Tuple[Any, Any], Dict[Any, Any]]] = None, **kwargs):
        self.url_base = url_base
        if seq is not None:
            if isinstance(seq, dict):
                for k, v in seq.items():
                    self[k] = v

            else:
                for k, v in seq:
                    self[k] = v

        for k, v in kwargs.items():
            self[k] = v

    def _dumps_tuple(self, t: Tuple[Any, ...]) -> str:
        return "(" + ", ".join(self._dumps_tuple(each_element) if isinstance(each_element, tuple) else json.dumps(each_element) for each_element in t) + ")"

    def _encodes_tuple(self, s: str) -> bool:
        return s.startswith("(") and s.endswith(")")

    def _loads_tuple(self, s: str) -> Tuple[Any, ...]:
        if not self._encodes_tuple(s):
            raise ValueError("string does not encode tuple")
        values = s[1:-1]
        return tuple(self._loads_tuple(each_string) if self._encodes_tuple(each_string) else json.loads(each_string) for each_string in values.split(", "))

    def __setitem__(self, k: KT, v: VT) -> None:
        k_json = self._dumps_tuple(k) if isinstance(k, tuple) else json.dumps(k)
        v_json = json.dumps(v)
        response = requests.put(self.url_base + WSDict._set, data={"key": k_json, "value": v_json})

    def __delitem__(self, k: KT) -> None:
        k_json = self._dumps_tuple(k) if isinstance(k, tuple) else json.dumps(k)
        response = requests.put(self.url_base + WSDict._pop, data={"key": k_json})

    def __getitem__(self, k: KT) -> VT_co:
        k_json = self._dumps_tuple(k) if isinstance(k, tuple) else json.dumps(k)
        response = requests.get(self.url_base + WSDict._get, params={"key": k_json})
        if not response.ok:
            raise KeyError("response from server not okay")

        response_dict = json.loads(response.text)
        if response_dict.get("msg") != "ok":
            raise KeyError(f"key {k_json:s} not found")

        value_str = response_dict.get("value")
        return json.loads(value_str)

    def _get_response_dict(self) -> Dict[str, str]:
        url = self.url_base + WSDict._complete
        response = requests.get(url)
        response_dict = json.loads(response.text)
        return response_dict

    def __len__(self) -> int:
        response_dict = self._get_response_dict()
        return len(response_dict)

    def __iter__(self) -> Iterator[T_co]:
        response_dict = self._get_response_dict()
        dictionary = {self._loads_tuple(k) if self._encodes_tuple(k) else json.loads(k): json.loads(v) for k, v in response_dict.items()}
        return iter(dictionary)


if __name__ == "__main__":
    d = WSDict("http://192.168.10.20:5000/")

    test_dict = {"a": 5, 5.3: [56, -3, [4.3, "w"]], (4, "b"): None}

    for _k, _v in test_dict.items():
        d[_k] = _v
        print({i: d[i] for i in iter(d)})

    for _k, _v in test_dict.items():
        del(d[_k])
        print({i: d[i] for i in iter(d)})

    print({i: d[i] for i in iter(d)})


