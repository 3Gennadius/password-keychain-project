SELECT u.user_id, u.username, p.password_hash
FROM users u
LEFT JOIN passwords p ON u.user_id = p.user_id;
