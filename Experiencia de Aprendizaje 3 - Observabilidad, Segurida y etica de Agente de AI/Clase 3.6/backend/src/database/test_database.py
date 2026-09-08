import os
from dotenv import load_dotenv

load_dotenv()


def test_env_vars_present():
    assert os.getenv("SUPABASE_URL") is not None, "SUPABASE_URL not set"
    assert os.getenv("SUPABASE_KEY") is not None, "SUPABASE_KEY not set"


def test_supabase_client_is_created():
    from src.database.client import supabase
    assert supabase is not None


def test_supabase_client_has_table_method():
    from src.database.client import supabase
    assert hasattr(supabase, "table")
