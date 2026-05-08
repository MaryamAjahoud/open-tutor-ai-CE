import os
import builtins
from pathlib import Path

backend_dir = Path(__file__).parent.parent
data_dir = backend_dir / "data"
data_dir.mkdir(exist_ok=True)

if "DATA_DIR" not in os.environ:
    os.environ["DATA_DIR"] = str(data_dir.absolute())

original_print = builtins.print

def custom_print(*args, **kwargs):
    return original_print(*args, **kwargs)

builtins.print = custom_print

import open_webui.utils.auth as auth
from fastapi import Depends, HTTPException, status

def patched_get_verified_user(user=Depends(auth.get_current_user)):
    if user.role not in {"user", "admin", "teacher", "parent"}:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=auth.ERROR_MESSAGES.ACCESS_PROHIBITED,
        )
    return user

auth.get_verified_user = patched_get_verified_user

import open_webui.utils.access_control as access_control
from open_webui.models.users import Users

original_has_access = access_control.has_access
original_has_permission = access_control.has_permission

def patched_has_access(user_id: str, type: str = "write", access_control_dict: dict = None) -> bool:
    user = Users.get_user_by_id(user_id)
    if user and user.role in ["teacher", "admin"]:
        return True
    return original_has_access(user_id, type, access_control_dict)

def patched_has_permission(user_id: str, permission_key: str, default_permissions: dict = {}) -> bool:
    user = Users.get_user_by_id(user_id)
    if user and user.role in ["teacher", "admin"]:
        return True
    return original_has_permission(user_id, permission_key, default_permissions)

access_control.has_access = patched_has_access
access_control.has_permission = patched_has_permission