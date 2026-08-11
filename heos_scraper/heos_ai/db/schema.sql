-- HEOS_DATABASE — esquema de la base de datos empresarial (FASE 2 del manual 040)
-- SQLite. Una empresa de alquiler de maquinaria pesada dirigida por IA.

PRAGMA foreign_keys = ON;

-- ============ EMPRESA ============
CREATE TABLE IF NOT EXISTS empresa (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    nombre TEXT NOT NULL,
    giro TEXT,
    moneda TEXT DEFAULT 'Gs.',
    objetivo_texto TEXT,
    organizacion_json TEXT,        -- organigrama / reglas de decisión
    created_at TEXT DEFAULT (datetime('now'))
);

-- ============ FLOTA ============
-- Una fila por máquina (expediente inteligente del Agente Flota IA)
CREATE TABLE IF NOT EXISTS flota (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,          -- MAQ-001
    marca TEXT,
    modelo TEXT,
    anho INTEGER,
    tipo TEXT,                             -- Excavadora, Retroexcavadora, Bulldozer...
    capacidad TEXT,
    valor_compra REAL,
    horas INTEGER DEFAULT 0,              -- horómetro
    odometro INTEGER DEFAULT 0,
    sucursal TEXT,
    ubicacion_gps TEXT,
    cliente_asignado TEXT,
    proyecto TEXT,
    operador TEXT,
    estado TEXT DEFAULT 'Disponible',     -- ver catálogo estados_posibles
    precio_hora REAL,                      -- tarifa de alquiler
    costo_hora REAL,                       -- costo operativo por hora
    ultimo_mantenimiento TEXT,
    proximo_mantenimiento TEXT,
    km_desde_sucursal INTEGER
);

-- ============ CLIENTES ============
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    tipo_contrato TEXT,           -- Mensual, Por obra, Spot
    precio_hora REAL,
    dias_pago INTEGER DEFAULT 30,
    historial_json TEXT,
    moroso INTEGER DEFAULT 0,
    rentabilidad REAL
);

-- ============ PERSONAL ============
CREATE TABLE IF NOT EXISTS personal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    rol TEXT,                      -- Operador, Tecnico, Administrativo
    certificado INTEGER DEFAULT 1,
    disponible INTEGER DEFAULT 1,
    productividad REAL DEFAULT 100,
    sucursal TEXT
);

-- ============ FINANZAS ============
CREATE TABLE IF NOT EXISTS finanzas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT DEFAULT (date('now')),
    concepto TEXT,
    tipo TEXT,                      -- Ingreso / Gasto
    categoria TEXT,                 -- Combustible, Repuestos, Salarios, Seguros, Financiacion, Alquiler
    monto REAL,
    cliente TEXT
);

-- ============ CONTRATOS (alquileres activos) ============
CREATE TABLE IF NOT EXISTS contratos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente TEXT,
    maquina TEXT,
    fecha_inicio TEXT,
    fecha_fin TEXT,
    precio_hora REAL,
    horas_contrato INTEGER,        -- horas estimadas del contrato
    estado TEXT DEFAULT 'Activo'
);

-- ============ MANTENIMIENTO ============
CREATE TABLE IF NOT EXISTS mantenimiento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    maquina TEXT,
    tipo TEXT,                      -- Preventivo / Correctivo
    fecha TEXT,
    costo REAL,
    detalle TEXT,
    estado TEXT DEFAULT 'Abierto'
);

-- ============ INCIDENTES ============
CREATE TABLE IF NOT EXISTS incidentes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT DEFAULT (date('now')),
    maquina TEXT,
    operador TEXT,
    cliente TEXT,
    causa TEXT,
    costo_estimado REAL,
    accion_correctiva TEXT,
    estado TEXT DEFAULT 'Abierto'
);

-- ============ ALERTAS (generadas por el motor de reglas) ============
CREATE TABLE IF NOT EXISTS alertas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT DEFAULT (datetime('now')),
    nivel TEXT,                     -- Critico / Alto / Medio / Bajo
    area TEXT,
    titulo TEXT,
    detalle TEXT,
    impacto_gs REAL,
    estado TEXT DEFAULT 'Activa'
);

-- ============ MEMORIA (5 niveles del CEO IA) ============
CREATE TABLE IF NOT EXISTS memoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nivel TEXT,                     -- Operativa / Tactica / Estrategica / Aprendizaje / Predictiva
    clave TEXT,
    valor_text TEXT,
    valor_num REAL,
    fecha TEXT DEFAULT (datetime('now'))
);

-- ============ RECOMENDACIONES ============
CREATE TABLE IF NOT EXISTS recomendaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT DEFAULT (datetime('now')),
    problema TEXT,
    causa TEXT,
    impacto_gs REAL,
    riesgo TEXT,
    accion TEXT,
    responsable TEXT,
    beneficio TEXT,
    confianza REAL,
    estado TEXT DEFAULT 'Pendiente'
);

-- Catálogo de estados de máquina (Documento 007)
CREATE TABLE IF NOT EXISTS estados_posibles (
    estado TEXT PRIMARY KEY
);
INSERT OR IGNORE INTO estados_posibles(estado) VALUES
 ('Disponible'),('Reservada'),('En traslado'),('Trabajando'),
 ('En mantenimiento preventivo'),('En mantenimiento correctivo'),
 ('Fuera de servicio'),('Vendida');
