# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from functools import wraps

from ansible.plugins.inventory.toml import HAS_TOML, toml_dumps, toml

from ansible.errors import (
    AnsibleError,
    AnsibleFilterError,
    AnsibleFilterTypeError,
)

from ansible.module_utils._text import to_text, to_native
from ansible.module_utils.common._collections_compat import Mapping


def _check_lib(func):
    @wraps(func)
    def with_check_lib(*args, **kwargs):
        if not HAS_TOML:
            raise AnsibleError('You need to install "toml" prior to running %s filter' % func.__name__)
        return func(*args, **kwargs)
    return with_check_lib


@_check_lib
def from_toml(s):
    if not isinstance(s, str):
        raise AnsibleFilterTypeError('from_toml requires a string, got %s' % type(s))

    try:
        return toml.loads(to_text(s, errors='surrogate_or_strict'))
    except Exception as e:
        raise AnsibleFilterError("from_toml - %s" % to_native(e), orig_exc=e)


@_check_lib
def to_toml(o):
    if not isinstance(o, Mapping):
        raise AnsibleFilterTypeError('to_toml requires a dict, got %s' % type(o))

    try:
        transformed = toml_dumps(o)
    except Exception as e:
        raise AnsibleFilterError("to_toml - %s" % to_native(e), orig_exc=e)
    return to_text(transformed, errors='surrogate_or_strict')


class FilterModule(object):

    def filters(self):
        return {
            'to_toml': to_toml,
            'from_toml': from_toml,
        }
