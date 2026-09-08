-- =============================================================
-- Productivity App — Database Schema
-- Run this in Supabase SQL Editor to create all tables
-- =============================================================

create table if not exists tasks (
  id           bigserial primary key,
  title        text        not null,
  description  text,
  status       text        not null default 'todo'
                           check (status in ('todo', 'doing', 'done')),
  importance   text        not null default 'low'
                           check (importance in ('low', 'high')),
  deadline     timestamptz,
  category     text        not null
                           check (category in ('ocio', 'familia', 'salud', 'dinero', 'casa', 'autocuidado', 'amor', 'trabajo')),
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now(),
  completed_at timestamptz
);

-- Auto-update updated_at on every row update
create or replace function update_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger tasks_updated_at
  before update on tasks
  for each row
  execute function update_updated_at();
