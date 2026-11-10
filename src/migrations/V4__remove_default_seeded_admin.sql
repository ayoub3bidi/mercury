-- Remove only the original default account; preserve an account whose password was changed.
DELETE FROM public.user
WHERE email = 'test@admin.com'
  AND password = '$5$rounds=535000$8ws.bvUTex83mhMg$ujSsZgI7F7OrtqVVYynHGH3d23SMuncuUIa4.aJ6kQD';
