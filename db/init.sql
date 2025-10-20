CREATE TABLE IF NOT EXISTS categories (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS items (
  id SERIAL PRIMARY KEY,
  url TEXT UNIQUE NOT NULL,
  url_norm TEXT UNIQUE,
  title TEXT,
  description TEXT,
  domain TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  category TEXT
);
CREATE TABLE IF NOT EXISTS item_meta (
  item_id INTEGER PRIMARY KEY REFERENCES items(id) ON DELETE CASCADE,
  meta_json JSONB
);
CREATE TABLE IF NOT EXISTS tags (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS item_tags (
  item_id INTEGER REFERENCES items(id) ON DELETE CASCADE,
  tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
  UNIQUE(item_id, tag_id)
);
-- Full-text GIN index
CREATE INDEX IF NOT EXISTS idx_items_fts ON items
USING GIN (to_tsvector('simple', coalesce(title,'') || ' ' || coalesce(description,'') || ' ' || coalesce(url,'')));
CREATE INDEX IF NOT EXISTS idx_items_domain ON items(domain);
CREATE INDEX IF NOT EXISTS idx_items_category ON items(category);
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);
