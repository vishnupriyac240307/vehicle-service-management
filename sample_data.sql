-- ============================================================================
-- TN SKILLS – Database Administration Back End – Oracle
-- Project Title: Vehicle Service Management Database System
-- Script: sample_data.sql (Sample Data Population)
-- Database Engine: Oracle Database (12c / 19c / 21c / 23c / XE / Free)
-- Tool: Oracle SQL Developer
-- ============================================================================

-- Ensure previous transactions are cleared
COMMIT;

-- ============================================================================
-- 1. INSERT CUSTOMERS
-- Safe practice: Never assume hardcoded IDs; Oracle identity columns auto-generate IDs.
-- ============================================================================
INSERT INTO CUSTOMER (customer_name, contact_number, email, address)
VALUES ('Arun Kumar', '9876543210', 'arun@example.com', 'Coimbatore');

INSERT INTO CUSTOMER (customer_name, contact_number, email, address)
VALUES ('Meena V', '9789012345', 'meena@example.com', 'Coimbatore');

-- Verify inserted customers
SELECT customer_id, customer_name, contact_number, email, address FROM CUSTOMER;

-- ============================================================================
-- 2. INSERT VEHICLES
-- Safe practice: Resolve customer_id dynamically using subqueries on unique email.
-- ============================================================================
INSERT INTO VEHICLE (vehicle_number, vehicle_type, vehicle_model, customer_id)
VALUES (
    'TN38AB1234', 
    'Car', 
    'Hyundai i20', 
    (SELECT customer_id FROM CUSTOMER WHERE email = 'arun@example.com')
);

INSERT INTO VEHICLE (vehicle_number, vehicle_type, vehicle_model, customer_id)
VALUES (
    'TN39CD5678', 
    'Bike', 
    'Royal Enfield Classic 350', 
    (SELECT customer_id FROM CUSTOMER WHERE email = 'meena@example.com')
);

-- Verify inserted vehicles with owner names
SELECT v.vehicle_id, v.vehicle_number, v.vehicle_type, v.vehicle_model, c.customer_name 
FROM VEHICLE v
JOIN CUSTOMER c ON v.customer_id = c.customer_id;

-- ============================================================================
-- 3. INSERT SERVICE RECORDS
-- Safe practice: 
--  - Resolve vehicle_id dynamically using subquery on unique vehicle_number.
--  - Use TO_DATE('YYYY-MM-DD', 'YYYY-MM-DD') to ensure NLS-independent date parsing.
-- ============================================================================

-- Service 1: Hyundai i20 – General Service – 2 August 2026 – Completed – ₹3,500
INSERT INTO SERVICE (vehicle_id, service_date, service_type, service_status, service_cost)
VALUES (
    (SELECT vehicle_id FROM VEHICLE WHERE vehicle_number = 'TN38AB1234'),
    TO_DATE('2026-08-02', 'YYYY-MM-DD'),
    'General Service',
    'Completed',
    3500.00
);

-- Service 2: Hyundai i20 – Oil Change – 10 September 2026 – Completed – ₹1,800
INSERT INTO SERVICE (vehicle_id, service_date, service_type, service_status, service_cost)
VALUES (
    (SELECT vehicle_id FROM VEHICLE WHERE vehicle_number = 'TN38AB1234'),
    TO_DATE('2026-09-10', 'YYYY-MM-DD'),
    'Oil Change',
    'Completed',
    1800.00
);

-- Service 3: Royal Enfield Classic 350 – Brake Service – 15 September 2026 – Pending – ₹2,200
INSERT INTO SERVICE (vehicle_id, service_date, service_type, service_status, service_cost)
VALUES (
    (SELECT vehicle_id FROM VEHICLE WHERE vehicle_number = 'TN39CD5678'),
    TO_DATE('2026-09-15', 'YYYY-MM-DD'),
    'Brake Service',
    'Pending',
    2200.00
);

-- Commit transaction to persist sample records
COMMIT;

-- Verify final service records
SELECT s.service_id, v.vehicle_number, s.service_type, s.service_date, s.service_status, s.service_cost
FROM SERVICE s
JOIN VEHICLE v ON s.vehicle_id = v.vehicle_id
ORDER BY s.service_id;
