-- Queries del detalle de pedidos (skill reporte-pedidos).
-- Cada query devuelve UNA fila; el alias de cada columna es el marcador {{...}} de assets/plantilla.html.
-- Parámetros: :desde y :hasta (YYYY-MM-DD), :cliente y :estado (texto o NULL = sin filtro).
-- El filtro de cliente ignora mayúsculas y tildes y acepta nombres parciales ("ana garcia" → "Ana García").
-- A diferencia de reporte-ventas, aquí se incluyen TODOS los estados salvo que se filtre por :estado.

-- name: Q1_detalle_pedidos
WITH d AS (
  SELECT p.id AS pedido, p.fecha, c.nombre AS cliente, c.ciudad, p.estado,
         pr.nombre AS producto, pr.categoria, dp.cantidad,
         CAST(ROUND(dp.precio_unitario) AS INTEGER)               AS precio_unitario,
         CAST(ROUND(dp.cantidad * dp.precio_unitario) AS INTEGER) AS subtotal
  FROM detalle_pedidos dp
  JOIN pedidos p    ON dp.pedido_id = p.id
  JOIN clientes c   ON p.cliente_id = c.id
  JOIN productos pr ON dp.producto_id = pr.id
  WHERE p.fecha BETWEEN :desde AND :hasta
    AND (:estado IS NULL OR p.estado = lower(trim(:estado)))
    AND (:cliente IS NULL OR
         lower(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(
           c.nombre, 'á','a'),'é','e'),'í','i'),'ó','o'),'ú','u'),'ñ','n'),
                     'Á','A'),'É','E'),'Í','I'),'Ó','O'),'Ú','U'),'Ñ','N'))
         LIKE '%' ||
         lower(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(
           trim(:cliente), 'á','a'),'é','e'),'í','i'),'ó','o'),'ú','u'),'ñ','n'),
                     'Á','A'),'É','E'),'Í','I'),'Ó','O'),'Ú','U'),'Ñ','N'))
         || '%')
  ORDER BY p.fecha, p.id, pr.nombre
)
SELECT
  COUNT(DISTINCT pedido)                                      AS TOTAL_PEDIDOS,  -- solo para que el agente detecte 0 filas
  CASE WHEN :cliente IS NULL THEN 'Todos'
       ELSE COALESCE((SELECT group_concat(n, ', ') FROM (SELECT DISTINCT cliente AS n FROM d ORDER BY n)),
                     'Sin coincidencias') END                 AS FILTRO_CLIENTE,
  CASE WHEN :estado IS NULL THEN 'Todos' ELSE lower(trim(:estado)) END AS FILTRO_ESTADO,
  group_concat(
    '<tr><td class="n">' || pedido || '</td><td>' || fecha || '</td><td>' || cliente ||
    '</td><td>' || ciudad || '</td><td><span class="estado ' || estado || '">' || estado ||
    '</span></td><td>' || producto || '</td><td>' || categoria ||
    '</td><td class="n num">' || cantidad || '</td><td class="n clp">' || precio_unitario ||
    '</td><td class="n clp">' || subtotal || '</td></tr>', '')
                                                              AS FILAS_DETALLE
FROM d;
