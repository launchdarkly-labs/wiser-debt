import os
import ldclient
from ldclient.config import Config
from ldclient import Context


def init_ld_client():
    sdk_key = os.environ.get("LAUNCHDARKLY_SDK_KEY", "")
    ldclient.set_config(Config(sdk_key))
    return ldclient.get()


def build_context(user_key="user-123", email="demo@wiser.com"):
    return Context.builder(user_key).kind("user").set("email", email).build()
