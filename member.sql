SELECT member.expiry_date, member.member_type, member.license_plate
FROM member
INNER JOIN parking_log ON member.license_plate = parking_log.license_plate

SELECT member.expiry_date, member.member_type, member.license_plate FROM member INNER JOIN parking_log ON member.license_plate = parking_log.license_plate ORDER BY date_in DESC LIMIT 1;