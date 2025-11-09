-- Direct SQL script to fix facial_evaluation table schema
-- Run this directly on your PostgreSQL database

-- Add missing columns to facial_evaluation table
ALTER TABLE facial_evaluation ADD COLUMN IF NOT EXISTS second_image_filename VARCHAR(255);
ALTER TABLE facial_evaluation ADD COLUMN IF NOT EXISTS morphed_image_filename VARCHAR(255);
ALTER TABLE facial_evaluation ADD COLUMN IF NOT EXISTS generation_id VARCHAR(36);
ALTER TABLE facial_evaluation ADD COLUMN IF NOT EXISTS admin_response TEXT;
ALTER TABLE facial_evaluation ADD COLUMN IF NOT EXISTS admin_id VARCHAR(36);
ALTER TABLE facial_evaluation ADD COLUMN IF NOT EXISTS credits_used INTEGER DEFAULT 20;

-- Add foreign key constraints (ignore errors if they already exist)
DO $$
BEGIN
    -- Add foreign key for generation_id
    BEGIN
        ALTER TABLE facial_evaluation 
        ADD CONSTRAINT fk_facial_evaluation_generation 
        FOREIGN KEY (generation_id) REFERENCES generation(id);
    EXCEPTION
        WHEN duplicate_object THEN
            -- Constraint already exists, ignore
            NULL;
    END;
    
    -- Add foreign key for admin_id
    BEGIN
        ALTER TABLE facial_evaluation 
        ADD CONSTRAINT fk_facial_evaluation_admin 
        FOREIGN KEY (admin_id) REFERENCES "user"(id);
    EXCEPTION
        WHEN duplicate_object THEN
            -- Constraint already exists, ignore
            NULL;
    END;
END $$;

-- Verify the table structure
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'facial_evaluation' 
ORDER BY ordinal_position;
