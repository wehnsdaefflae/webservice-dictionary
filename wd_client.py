import json
from urllib.parse import quote
from collections.abc import MutableMapping
from typing import Iterator, TypeVar, Dict, Any, Tuple, Optional, Union
import requests

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
        self.url_base = "http://127.0.0.1:5000/"
        if seq is not None:
            if isinstance(seq, dict):
                for k, v in seq.items():
                    self[k] = v

            else:
                for k, v in seq:
                    self[k] = v

        for k, v in kwargs.items():
            self[k] = v

    def __setitem__(self, k: KT, v: VT) -> None:
        k_json = json.dumps(k)
        v_json = json.dumps(v)
        url = self.url_base + WSDict._set + f"{quote(k_json):s}/{quote(v_json):s}"
        response = requests.get(url)

    def __delitem__(self, v: KT) -> None:
        k_json = json.dumps(v)
        url = self.url_base + WSDict._pop + f"{quote(k_json):s}"
        response = requests.get(url)

    def __getitem__(self, k: KT) -> VT_co:
        k_json = json.dumps(k)
        url = self.url_base + WSDict._get + f"{quote(k_json):s}"
        response = requests.get(url)
        if not response.ok:
            return None
        response_dict = json.loads(response.text)
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
        dictionary = {json.loads(k): json.loads(v) for k, v in response_dict.items()}
        return iter(dictionary)


if __name__ == "__main__":
    #s = '"asef"'
    #print(unquote(s))
    #print(quote(s))
    d = WSDict("http://192.168.10.20:5000/")
    d["testkey"] = "testvalue"
    d[3] = [4, 6, 7]

    print()
