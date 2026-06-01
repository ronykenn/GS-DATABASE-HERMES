-- Consulta 1: Quantidade de objetos orbitais por tipo
SELECT object_type, COUNT(*) AS total_objects
FROM HERMES_ORBITAL_OBJECTS
GROUP BY object_type
ORDER BY total_objects DESC;

-- Consulta 2: Media, minimo e maximo do risco de colisao por zona orbital
SELECT orbit_zone,
       ROUND(AVG(collision_risk_score), 2) AS avg_collision_risk,
       MIN(collision_risk_score) AS min_collision_risk,
       MAX(collision_risk_score) AS max_collision_risk
FROM HERMES_ORBITAL_OBJECTS
GROUP BY orbit_zone
ORDER BY avg_collision_risk DESC;

-- Consulta 3: Ranking dos 10 objetos com maior risco de colisao
SELECT object_id, object_name, object_type, orbit_zone, collision_risk_score, priority_level, recommended_action
FROM HERMES_ORBITAL_OBJECTS
ORDER BY collision_risk_score DESC
FETCH FIRST 10 ROWS ONLY;

-- Consulta 4: Quantidade de missoes recomendadas por tipo de acao
SELECT recommended_action, COUNT(*) AS total_missions
FROM HERMES_ORBITAL_OBJECTS
GROUP BY recommended_action
ORDER BY total_missions DESC;

-- Consulta 5: Consumo total de combustivel estimado por nivel de prioridade
SELECT priority_level, ROUND(SUM(fuel_required_kg), 2) AS total_fuel_required_kg
FROM HERMES_ORBITAL_OBJECTS
GROUP BY priority_level
ORDER BY total_fuel_required_kg DESC;

-- Consulta 6: Lancamentos SpaceX bem-sucedidos e malsucedidos por ano
SELECT EXTRACT(YEAR FROM launch_date_utc) AS launch_year,
       SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) AS successful_launches,
       SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) AS failed_launches
FROM HERMES_SPACEX_LAUNCHES
GROUP BY EXTRACT(YEAR FROM launch_date_utc)
ORDER BY launch_year;

-- Consulta 7: Ultimas posicoes registradas da ISS
SELECT position_id, latitude, longitude, collected_at
FROM HERMES_ISS_POSITION
ORDER BY collected_at DESC
FETCH FIRST 10 ROWS ONLY;
