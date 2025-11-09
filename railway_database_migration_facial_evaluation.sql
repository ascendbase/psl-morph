-- Railway Database Migration for Facial Evaluation Feature
-- Run this directly in Railway's PostgreSQL console

-- Fix the status column size issue
ALTER TABLE facial_evaluations 
ALTER COLUMN status TYPE VARCHAR(20);

-- Verify the change
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'facial_evaluations' 
AND column_name = 'status';

-- Test that we can insert proper status values
-- (This is just a test - will be rolled back)
BEGIN;
INSERT INTO facial_evaluations 
(id, user_id, status, created_at, credits_used) 
VALUES 
('test-migration-id', 'test-user-id', 'Pending', NOW(), 20);
ROLLBACK;

-- Show success message
SELECT 'Facial Evaluation database migration completed successfully!' as result;
