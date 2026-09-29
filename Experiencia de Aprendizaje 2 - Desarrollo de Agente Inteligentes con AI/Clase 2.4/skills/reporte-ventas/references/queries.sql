-- Queries del reporte de ventas (skill reporte-ventas).
-- Cada query devuelve UNA fila; el alias de cada columna es el marcador {{...}} de assets/plantilla.html.
-- Parámetros: :desde y :hasta (YYYY-MM-DD). Solo pedidos 'entregado', salvo Q7.

-- name: Q1_kpis
SELECT
  CAST(ROUND(SUM(dp.cantidad * dp.precio_unitario)) AS INTEGER)                        AS TOTAL_VENDIDO,
  COUNT(DISTINCT p.id)                                                                 AS PEDIDOS_ENTREGADOS,
  CAST(ROUND(SUM(dp.cantidad * dp.precio_unitario) / COUNT(DISTINCT p.id)) AS INTEGER) AS TICKET_PROMEDIO,
  SUM(dp.cantidad)                                                                     AS UNIDADES_VENDIDAS
FROM detalle_pedidos dp
JOIN pedidos p ON dp.pedido_id = p.id
WHERE p.estado = 'entregado' AND p.fecha BETWEEN :desde AND :hasta;

-- name: Q2_ventas_por_mes
WITH m AS (
  SELECT strftime('%Y-%m', p.fecha) AS mes,
         CAST(ROUND(SUM(dp.cantidad * dp.precio_unitario)) AS INTEGER) AS total
  FROM detalle_pedidos dp
  JOIN pedidos p ON dp.pedido_id = p.id
  WHERE p.estado = 'entregado' AND p.fecha BETWEEN :desde AND :hasta
  GROUP BY mes
)
SELECT
  (SELECT json_group_array(mes)   FROM (SELECT mes, total FROM m ORDER BY mes)) AS MESES_LABELS,
  (SELECT json_group_array(total) FROM (SELECT mes, total FROM m ORDER BY mes)) AS MESES_DATA,
  (SELECT mes   FROM m ORDER BY total DESC LIMIT 1) AS MEJOR_MES,
  (SELECT total FROM m ORDER BY total DESC LIMIT 1) AS MEJOR_MES_TOTAL,
  (SELECT mes   FROM m ORDER BY total ASC  LIMIT 1) AS PEOR_MES,
  (SELECT total FROM m ORDER BY total ASC  LIMIT 1) AS PEOR_MES_TOTAL;

-- name: Q3_ranking_clientes
WITH r AS (
  SELECT c.nombre, c.ciudad,
         COUNT(DISTINCT p.id) AS pedidos,
         CAST(ROUND(SUM(dp.cantidad * dp.precio_unitario)) AS INTEGER) AS total
  FROM clientes c
  JOIN pedidos p ON c.id = p.cliente_id
  JOIN detalle_pedidos dp ON p.id = dp.pedido_id
  WHERE p.estado = 'entregado' AND p.fecha BETWEEN :desde AND :hasta
  GROUP BY c.id
)
SELECT group_concat(
         '<tr><td>' || pos || '</td><td>' || nombre || '</td><td>' || ciudad ||
         '</td><td class="n num">' || pedidos || '</td><td class="n clp">' || total || '</td></tr>', '')
       AS FILAS_CLIENTES
FROM (SELECT ROW_NUMBER() OVER (ORDER BY total DESC) AS pos, * FROM r ORDER BY total DESC);

-- name: Q4_ranking_productos
WITH r AS (
  SELECT pr.nombre, pr.categoria,
         SUM(dp.cantidad) AS unidades,
         CAST(ROUND(SUM(dp.cantidad * dp.precio_unitario)) AS INTEGER) AS total
  FROM detalle_pedidos dp
  JOIN productos pr ON dp.producto_id = pr.id
  JOIN pedidos p ON dp.pedido_id = p.id
  WHERE p.estado = 'entregado' AND p.fecha BETWEEN :desde AND :hasta
  GROUP BY pr.id
)
SELECT group_concat(
         '<tr><td>' || pos || '</td><td>' || nombre || '</td><td>' || categoria ||
         '</td><td class="n num">' || unidades || '</td><td class="n clp">' || total || '</td></tr>', '')
       AS FILAS_PRODUCTOS
FROM (SELECT ROW_NUMBER() OVER (ORDER BY unidades DESC) AS pos, * FROM r ORDER BY unidades DESC);

-- name: Q5_ventas_por_categoria
SELECT json_group_array(categoria) AS CATEGORIAS_LABELS,
       json_group_array(total)     AS CATEGORIAS_DATA
FROM (
  SELECT pr.categoria,
         CAST(ROUND(SUM(dp.cantidad * dp.precio_unitario)) AS INTEGER) AS total
  FROM detalle_pedidos dp
  JOIN productos pr ON dp.producto_id = pr.id
  JOIN pedidos p ON dp.pedido_id = p.id
  WHERE p.estado = 'entregado' AND p.fecha BETWEEN :desde AND :hasta
  GROUP BY pr.categoria
  ORDER BY total DESC
);

-- name: Q6_ventas_por_ciudad
SELECT json_group_array(ciudad) AS CIUDADES_LABELS,
       json_group_array(total)  AS CIUDADES_DATA
FROM (
  SELECT c.ciudad,
         CAST(ROUND(SUM(dp.cantidad * dp.precio_unitario)) AS INTEGER) AS total
  FROM clientes c
  JOIN pedidos p ON c.id = p.cliente_id
  JOIN detalle_pedidos dp ON p.id = dp.pedido_id
  WHERE p.estado = 'entregado' AND p.fecha BETWEEN :desde AND :hasta
  GROUP BY c.ciudad
  ORDER BY total DESC
);

-- name: Q7_pedidos_por_estado
SELECT json_group_array(estado)  AS ESTADOS_LABELS,
       json_group_array(pedidos) AS ESTADOS_DATA
FROM (
  SELECT estado, COUNT(*) AS pedidos
  FROM pedidos
  WHERE fecha BETWEEN :desde AND :hasta
  GROUP BY estado
  ORDER BY pedidos DESC
);
