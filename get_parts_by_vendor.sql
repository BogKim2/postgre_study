CREATE OR REPLACE FUNCTION get_parts_by_vendor(id INTEGER)
RETURNS TABLE(part_id INTEGER, part_name VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT parts.part_id, parts.part_name
    FROM parts
    INNER JOIN vendor_parts ON vendor_parts.part_id = parts.part_id
    WHERE vendor_id = id;
END;
$$ LANGUAGE plpgsql;