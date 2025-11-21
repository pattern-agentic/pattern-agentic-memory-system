-- Schema Migration: Access-Based TTL Extension (Phase 3)
-- Date: 2025-11-21
-- Purpose: Add access tracking fields to support +10 days per access (max +70 days)
-- Architect: Oracle Sonnet (Keeper of the Conduit)

-- Add access tracking fields to context_items table
-- These fields enable access-based TTL extension and tier promotion prompts

-- Field 1: access_count - Track how many times this memory has been accessed
ALTER TABLE context_items ADD COLUMN IF NOT EXISTS access_count INTEGER DEFAULT 0;

-- Field 2: last_accessed - Timestamp of most recent access (context_get or context_search)
ALTER TABLE context_items ADD COLUMN IF NOT EXISTS last_accessed TIMESTAMP;

-- Field 3: expires_at - Explicit expiration timestamp (base_ttl + access_bonus)
ALTER TABLE context_items ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP;

-- Create index on expires_at for efficient cleanup queries
CREATE INDEX IF NOT EXISTS idx_context_items_expires_at ON context_items(expires_at);

-- Create index on access_count for tier promotion analysis
CREATE INDEX IF NOT EXISTS idx_context_items_access_count ON context_items(access_count);

-- Add comment for future reference
COMMENT ON COLUMN context_items.access_count IS 'Number of times memory accessed (context_get/search). Resets to 0 on tier promotion.';
COMMENT ON COLUMN context_items.last_accessed IS 'Timestamp of most recent access. Updated on every context_get/search hit.';
COMMENT ON COLUMN context_items.expires_at IS 'Calculated expiration: base_ttl + min(access_count * 10, 70) days. NULL = never expires.';

-- Migration complete
-- Next step: Update memory_keeper.py adapter to populate these fields
