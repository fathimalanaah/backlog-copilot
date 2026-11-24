-- Backlog Copilot: one-time Supabase setup (run in Supabase > SQL Editor).
-- Stores approved stories only (PRD US-12). Demo data is fictional.

create table if not exists public.saved_stories (
  id bigserial primary key,
  project text not null,
  story_id text not null,
  payload jsonb not null,
  saved_at timestamptz not null default now()
);

alter table public.saved_stories enable row level security;

-- Newer Supabase projects do not auto-grant new tables to the public (anon) role.
-- Grant insert + read only (no update/delete).
grant select, insert on public.saved_stories to anon;
grant usage, select on sequence public.saved_stories_id_seq to anon;

-- Single-user portfolio demo: the public (anon) key may insert and read rows,
-- but cannot update or delete them, so saved approvals are never altered.
-- A production version would require sign-in and per-user policies.
drop policy if exists "demo insert" on public.saved_stories;
drop policy if exists "demo read" on public.saved_stories;
create policy "demo insert" on public.saved_stories for insert to anon with check (true);
create policy "demo read" on public.saved_stories for select to anon using (true);
