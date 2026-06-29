-- Aether Radar SaaS database schema draft
-- Target: Postgres / Supabase

create table if not exists entities (
  id text primary key,
  name text not null,
  cn text not null,
  literal text,
  type text not null,
  category text not null,
  summary text not null,
  value text,
  url text,
  github_repo text,
  heat_level text,
  risk_level text,
  source_confidence text,
  source_type text,
  review_status text,
  pricing text,
  license text,
  commercial_use text,
  china_usability text,
  api_support text,
  mcp_support text,
  data_privacy text,
  recommended_for text,
  risk_note text,
  last_verified_at date,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table if not exists categories (
  id text primary key,
  name text not null,
  description text
);

create table if not exists risk_scores (
  id text primary key,
  name text not null,
  description text,
  severity text not null
);

create table if not exists github_metrics (
  id bigserial primary key,
  entity_id text references entities(id) on delete cascade,
  repo text not null,
  stars int,
  forks int,
  open_issues int,
  watchers int,
  license text,
  archived boolean,
  pushed_at timestamptz,
  fetched_at timestamptz default now()
);

create table if not exists scenarios (
  id text primary key,
  name text not null,
  user_profile text,
  difficulty text,
  cost text,
  local_possible text,
  risk text,
  path text
);

create table if not exists scenario_tools (
  scenario_id text references scenarios(id) on delete cascade,
  entity_id text references entities(id) on delete cascade,
  sort_order int default 0,
  primary key (scenario_id, entity_id)
);

create table if not exists users (
  id uuid primary key,
  email text unique,
  display_name text,
  plan text default 'free',
  created_at timestamptz default now()
);

create table if not exists user_stacks (
  id uuid primary key,
  user_id uuid references users(id) on delete cascade,
  name text not null,
  goal text,
  sensitivity text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table if not exists user_stack_items (
  stack_id uuid references user_stacks(id) on delete cascade,
  entity_id text references entities(id) on delete cascade,
  notes text,
  primary key (stack_id, entity_id)
);

create table if not exists api_keys (
  id uuid primary key,
  user_id uuid references users(id) on delete cascade,
  key_hash text not null,
  scope text not null,
  last_used_at timestamptz,
  created_at timestamptz default now(),
  revoked_at timestamptz
);

create table if not exists audit_logs (
  id bigserial primary key,
  actor_user_id uuid,
  action text not null,
  target_type text,
  target_id text,
  metadata jsonb default '{}'::jsonb,
  created_at timestamptz default now()
);
