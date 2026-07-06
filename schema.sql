-- ============================================================
-- English Studio  |  Schema Supabase
-- Cole tudo isto no Supabase → SQL Editor → New query → Run
-- ============================================================

create table if not exists cards (
  id          text primary key,
  tipo        text not null,          -- 'questao' | 'flashcard' | 'conceito'
  topico      text not null,
  subtopico   text default '',
  dificuldade int  default 3,         -- 1 (facil) .. 5 (dificil)
  tags        jsonb default '[]'::jsonb,
  fonte       text default '',
  enunciado   text,                   -- para 'questao'
  opcoes      jsonb,                  -- para 'questao'
  correta     int,                    -- para 'questao' (indice 0..n)
  frente      text,                   -- para flashcard/conceito
  verso       text,
  explicacao  text,
  imagem      text                    -- caminho relativo p/ card visual (assets/img/...)
);

-- migração de bases antigas:
alter table cards add column if not exists imagem text;

-- Estado FSRS por usuario e card
create table if not exists progress (
  user_id    text not null,
  card_id    text not null,
  state      text default 'new',     -- new | learning | review | relearning
  step       int  default 0,
  stability  real default 0,
  difficulty real default 0,
  reps       int  default 0,
  lapses     int  default 0,
  due        timestamptz,
  last       timestamptz,
  suspended  boolean default false,
  primary key (user_id, card_id)
);

-- Log de cada review FSRS
create table if not exists reviews (
  id         bigserial primary key,
  user_id    text not null,
  card_id    text not null,
  rating     text,                    -- again | hard | good | easy
  prev_state text,
  state      text,
  stability  real,
  difficulty real,
  elapsed_ms int,
  ts         timestamptz default now()
);

-- Historico de respostas a questoes (por card, com modo e tempo)
create table if not exists answers (
  id         bigserial primary key,
  user_id    text not null,
  card_id    text,
  topico     text,
  ok         boolean,
  mode       text,                    -- practice | mock | review | errors
  elapsed_ms int,
  confidence text,                    -- sure | unsure (metacognition)
  cause      text,                    -- content | misread | calc | time (error autopsy)
  ts         timestamptz default now()
);

-- migração de bases v2 antigas:
alter table answers add column if not exists confidence text;
alter table answers add column if not exists cause text;

-- Historico de simulados (com detalhe por topico)
create table if not exists mocks (
  id         bigserial primary key,
  user_id    text not null,
  n          int,
  correct    int,
  pct        real,
  duration_s int,
  detail     jsonb default '{}'::jsonb,
  ts         timestamptz default now()
);

-- Cards sinalizados como suspeitos/confusos pelo usuario
create table if not exists flags (
  id      bigserial primary key,
  user_id text not null,
  card_id text,
  reason  text,
  ts      timestamptz default now()
);

-- Preferencias do usuario (data da prova, metas, retencao FSRS)
create table if not exists settings (
  user_id    text primary key,
  exam_date  text,
  retention  real default 0.9,
  daily_new  int  default 10,
  daily_goal int  default 20,
  updated_at timestamptz default now()
);

-- ---- Acesso (app pessoal: libera leitura/escrita via anon key) ----
alter table cards    enable row level security;
alter table progress enable row level security;
alter table reviews  enable row level security;
alter table answers  enable row level security;
alter table mocks    enable row level security;
alter table settings enable row level security;

create policy "anon_all_cards"    on cards    for all using (true) with check (true);
create policy "anon_all_progress" on progress for all using (true) with check (true);
create policy "anon_all_reviews"  on reviews  for all using (true) with check (true);
create policy "anon_all_answers"  on answers  for all using (true) with check (true);
create policy "anon_all_mocks"    on mocks    for all using (true) with check (true);
create policy "anon_all_settings" on settings for all using (true) with check (true);
