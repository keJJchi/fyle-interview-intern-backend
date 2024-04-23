-- Write query to find the number of grade A's given by the teacher who has graded the most assignments
-- 
SELECT COUNT(*) AS num_a_grades
FROM assignments
WHERE teacher_id = (
    SELECT teacher_id
    FROM (
        SELECT teacher_id, COUNT(*) AS num_assignments
        FROM assignments
        GROUP BY teacher_id
        ORDER BY num_assignments DESC
        LIMIT 1
    ) AS most_assignments
)
AND grade = 'A';
