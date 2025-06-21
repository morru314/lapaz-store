from supabase import create_client
import os

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")

supabase = create_client(supabase_url, supabase_key)