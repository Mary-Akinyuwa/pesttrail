-- PestTrail Supabase RLS Fix
-- Run this in: Supabase Dashboard → SQL Editor → New Query → Paste → Run
--
-- What this does:
--   1. Enables Row Level Security on the visits table
--   2. Allows the app (anon role) to INSERT visit records (needed for analytics logging)
--   3. Blocks anon SELECT, UPDATE, DELETE — only the service_role key can read/modify data
--
-- After running this SQL, add your service role key to Streamlit Secrets:
--   SUPABASE_SERVICE_KEY = "eyJ..."   ← from Supabase → Settings → API → service_role key
--   Keep this key private. Never commit it to GitHub.

-- Step 1: Enable RLS
ALTER TABLE visits ENABLE ROW LEVEL SECURITY;

-- Step 2: Allow INSERT for the app (anon key logs visit records)
CREATE POLICY "anon_can_insert_visits"
ON visits
FOR INSERT
TO anon
WITH CHECK (true);

-- Step 3: No SELECT/UPDATE/DELETE policy for anon = those are blocked by default
-- The service_role key used in admin.py bypasses RLS entirely, so admin reads still work.
