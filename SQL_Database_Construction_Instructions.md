### Requirements:
- At least 75 customers and 150 reservations, spanning at least one quarter
- Reasonable number of records for other tables 
- All tables must be normalized to **3NF (Third Normal Form)**
- Database should be optimized for **transactional use**

### Commands track:
-- Create the database
CREATE DATABASE hotel_last_resort;
USE hotel_last_resort;
```

#### 2.1 Room Type Table
```sql
CREATE TABLE room_type (
    roomTypeId INT PRIMARY KEY AUTO_INCREMENT,
    roomType VARCHAR(50) NOT NULL UNIQUE,
    baseRate DECIMAL(10, 2) NOT NULL,
    maxOccupancy INT NOT NULL,
    description TEXT,
    CONSTRAINT chk_baseRate CHECK (baseRate > 0),
    CONSTRAINT chk_maxOccupancy CHECK (maxOccupancy > 0)
);
```

#### 2.2 Room Status Table
```sql
CREATE TABLE room_status (
    roomStatusId INT PRIMARY KEY AUTO_INCREMENT,
    status VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);
```

#### 2.3 Building Table
```sql
CREATE TABLE building (
    buildingId INT PRIMARY KEY AUTO_INCREMENT,
    buildingName VARCHAR(100) NOT NULL UNIQUE,
    address TEXT,
    totalFloors INT,
    CONSTRAINT chk_totalFloors CHECK (totalFloors > 0)
);
```

#### 2.4 Wing Table (if applicable)
```sql
CREATE TABLE wing (
    wingId INT PRIMARY KEY AUTO_INCREMENT,
    wingName VARCHAR(100) NOT NULL,
    buildingId INT NOT NULL,
    FOREIGN KEY (buildingId) REFERENCES building(buildingId) ON DELETE CASCADE,
    UNIQUE KEY unique_wing (buildingId, wingName)
);
```

#### 2.5 Floor Table (if applicable)
```sql
CREATE TABLE floor (
    floorId INT PRIMARY KEY AUTO_INCREMENT,
    floorNo INT NOT NULL,
    buildingId INT NOT NULL,
    wingId INT,
    FOREIGN KEY (buildingId) REFERENCES building(buildingId) ON DELETE CASCADE,
    FOREIGN KEY (wingId) REFERENCES wing(wingId) ON DELETE SET NULL,
    UNIQUE KEY unique_floor (buildingId, wingId, floorNo)
);
```

### Step 3: Create Core Entity Tables

#### 3.1 Room Table
```sql
CREATE TABLE room (
    roomId INT PRIMARY KEY AUTO_INCREMENT,
    roomNumber VARCHAR(20) NOT NULL,
    buildingId INT NOT NULL,
    wingId INT,
    floorId INT,
    roomTypeId INT NOT NULL,
    roomStatusId INT NOT NULL,
    squareFootage DECIMAL(8, 2),
    FOREIGN KEY (buildingId) REFERENCES building(buildingId) ON DELETE CASCADE,
    FOREIGN KEY (wingId) REFERENCES wing(wingId) ON DELETE SET NULL,
    FOREIGN KEY (floorId) REFERENCES floor(floorId) ON DELETE SET NULL,
    FOREIGN KEY (roomTypeId) REFERENCES room_type(roomTypeId) ON DELETE RESTRICT,
    FOREIGN KEY (roomStatusId) REFERENCES room_status(roomStatusId) ON DELETE RESTRICT,
    UNIQUE KEY unique_room (buildingId, roomNumber)
);
```

#### 3.2 Customer Table
```sql
CREATE TABLE customer (
    customerId INT PRIMARY KEY AUTO_INCREMENT,
    firstName VARCHAR(100) NOT NULL,
    lastName VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    address TEXT,
    dateOfBirth DATE,
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_name (lastName, firstName)
);
```

#### 3.3 Staff Table
```sql
CREATE TABLE staff (
    staffId INT PRIMARY KEY AUTO_INCREMENT,
    firstName VARCHAR(100) NOT NULL,
    lastName VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    role VARCHAR(50) NOT NULL,
    department VARCHAR(50),
    hireDate DATE NOT NULL,
    isActive BOOLEAN DEFAULT TRUE,
    INDEX idx_role (role),
    INDEX idx_email (email)
);
```

### Step 4: Create Relationship Tables

#### 4.1 Reservation Table
```sql
CREATE TABLE reservation (
    reservationId INT PRIMARY KEY AUTO_INCREMENT,
    customerId INT NOT NULL,
    roomId INT NOT NULL,
    startDateTime DATETIME NOT NULL,
    endDateTime DATETIME NOT NULL,
    days INT NOT NULL,
    totalRate DECIMAL(10, 2) NOT NULL,
    depositStatus VARCHAR(50),
    status VARCHAR(50) DEFAULT 'confirmed',
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customerId) REFERENCES customer(customerId) ON DELETE RESTRICT,
    FOREIGN KEY (roomId) REFERENCES room(roomId) ON DELETE RESTRICT,
    CONSTRAINT chk_dates CHECK (endDateTime > startDateTime),
    CONSTRAINT chk_totalRate CHECK (totalRate >= 0),
    INDEX idx_customer (customerId),
    INDEX idx_room (roomId),
    INDEX idx_dates (startDateTime, endDateTime)
);
```

#### 4.2 Meeting Space Table (if applicable)
```sql
CREATE TABLE meeting_space (
    roomId INT PRIMARY KEY,
    spaceType VARCHAR(50) NOT NULL,
    capacity INT NOT NULL,
    hasProjector BOOLEAN DEFAULT FALSE,
    hasWhiteboard BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (roomId) REFERENCES room(roomId) ON DELETE CASCADE,
    CONSTRAINT chk_capacity CHECK (capacity > 0)
);
```

#### 4.3 Event Table
```sql
CREATE TABLE event (
    eventId INT PRIMARY KEY AUTO_INCREMENT,
    reservationId INT NOT NULL,
    eventName VARCHAR(200) NOT NULL,
    eventDate DATETIME NOT NULL,
    estNoGuest INT NOT NULL,
    eventType VARCHAR(50),
    FOREIGN KEY (reservationId) REFERENCES reservation(reservationId) ON DELETE CASCADE,
    CONSTRAINT chk_estNoGuest CHECK (estNoGuest > 0),
    INDEX idx_reservation (reservationId)
);
```

#### 4.4 Customer Requests Table
```sql
CREATE TABLE customer_requests (
    requestId INT PRIMARY KEY AUTO_INCREMENT,
    customerId INT NOT NULL,
    reservationId INT,
    requestType VARCHAR(100) NOT NULL,
    description TEXT,
    depositStatus VARCHAR(50),
    resolved CHAR(1) DEFAULT 'N',
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolvedAt DATETIME,
    FOREIGN KEY (customerId) REFERENCES customer(customerId) ON DELETE CASCADE,
    FOREIGN KEY (reservationId) REFERENCES reservation(reservationId) ON DELETE SET NULL,
    CONSTRAINT chk_resolved CHECK (resolved IN ('Y', 'N')),
    INDEX idx_customer (customerId),
    INDEX idx_resolved (resolved)
);
```

### Step 5: Create Access Control Tables

#### 5.1 Readers Table
```sql
CREATE TABLE readers (
    readersId INT PRIMARY KEY AUTO_INCREMENT,
    location VARCHAR(100) NOT NULL,
    readerType VARCHAR(50),
    isActive BOOLEAN DEFAULT TRUE
);
```

#### 5.2 Staff Card Assignment Table
```sql
CREATE TABLE staff_card_assignment (
    staffcardId INT PRIMARY KEY AUTO_INCREMENT,
    staffId INT NOT NULL,
    cardNumber VARCHAR(50) UNIQUE NOT NULL,
    issuedDate DATE NOT NULL,
    expiryDate DATE,
    isActive BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (staffId) REFERENCES staff(staffId) ON DELETE CASCADE,
    INDEX idx_staff (staffId),
    INDEX idx_cardNumber (cardNumber)
);
```

#### 5.3 Reading Info Table
```sql
CREATE TABLE reading_info (
    readingId INT PRIMARY KEY AUTO_INCREMENT,
    staffcardId INT NOT NULL,
    readerID INT NOT NULL,
    swipeDateTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    accessGranted BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (staffcardId) REFERENCES staff_card_assignment(staffcardId) ON DELETE CASCADE,
    FOREIGN KEY (readerID) REFERENCES readers(readersId) ON DELETE RESTRICT,
    INDEX idx_staffcard (staffcardId),
    INDEX idx_reader (readerID),
    INDEX idx_datetime (swipeDateTime)
);
```

### Step 6: Create Supporting Tables

#### 6.1 Adjacency Table (for room combinations)
```sql
CREATE TABLE adjacency (
    adjacencyId INT PRIMARY KEY AUTO_INCREMENT,
    roomId INT NOT NULL,
    adjacentRoomId INT NOT NULL,
    FOREIGN KEY (roomId) REFERENCES room(roomId) ON DELETE CASCADE,
    FOREIGN KEY (adjacentRoomId) REFERENCES room(roomId) ON DELETE CASCADE,
    CONSTRAINT chk_different_rooms CHECK (roomId != adjacentRoomId),
    UNIQUE KEY unique_adjacency (roomId, adjacentRoomId)
);
```

---

## Step 7: Data Population Guidelines

### 7.1 Populate Lookup Tables First

```sql
-- Room Types
INSERT INTO room_type (roomType, baseRate, maxOccupancy, description) VALUES
('Standard', 150.00, 2, 'Standard room with basic amenities'),
('Deluxe', 250.00, 4, 'Deluxe room with enhanced amenities'),
('Suite', 400.00, 6, 'Spacious suite with separate living area'),
('Meeting Room Small', 200.00, 10, 'Small meeting space'),
('Meeting Room Large', 500.00, 50, 'Large meeting space');

-- Room Status
INSERT INTO room_status (status, description) VALUES
('available', 'Room is available for booking'),
('occupied', 'Room is currently occupied'),
('maintenance', 'Room is under maintenance'),
('renovation', 'Room is being renovated'),
('reconstruction', 'Room is being reconstructed');

-- Buildings
INSERT INTO building (buildingName, address, totalFloors) VALUES
('Main Building', '123 Hotel Street', 10),
('Annex Building', '125 Hotel Street', 5);
```

### 7.2 Populate Core Tables

**Customers (Minimum 50-75):**
- Create at least 50 customers (B level) or 75 customers (A level)
- Include diverse names, emails, and contact information
- Ensure some customers have multiple reservations

**Rooms:**
- Create rooms across different buildings, floors, and types
- Mix room statuses (most should be 'available')
- Include meeting spaces if applicable

**Reservations (Minimum 100-150):**
- Create at least 100 reservations (B level) or 150 reservations (A level)
- **CRITICAL**: Span at least one quarter (3 months) of dates
- Distribute reservations across different customers and rooms
- Include various room types
- Calculate `days` and `totalRate` appropriately
- Ensure date ranges don't overlap for the same room (unless status allows)

**Example Reservation Population:**
```sql
-- Example: Create reservations spanning Q1 2024 (Jan-Mar)
-- Ensure dates span at least one quarter
INSERT INTO reservation (customerId, roomId, startDateTime, endDateTime, days, totalRate, depositStatus, status)
SELECT 
    c.customerId,
    r.roomId,
    DATE_ADD('2024-01-01', INTERVAL FLOOR(RAND() * 90) DAY) + INTERVAL FLOOR(RAND() * 14) HOUR,
    DATE_ADD(startDateTime, INTERVAL (1 + FLOOR(RAND() * 7)) DAY),
    DATEDIFF(endDateTime, startDateTime),
    rt.baseRate * DATEDIFF(endDateTime, startDateTime) * (0.9 + RAND() * 0.2),
    CASE WHEN RAND() > 0.5 THEN 'paid' ELSE 'pending' END,
    'confirmed'
FROM customer c
CROSS JOIN room r
JOIN room_type rt ON rt.roomTypeId = r.roomTypeId
WHERE r.roomStatusId = (SELECT roomStatusId FROM room_status WHERE status = 'available')
LIMIT 150; -- Adjust based on A/B level requirement
```

### 7.3 Populate Supporting Data

- **Staff**: Create staff members with various roles
- **Staff Card Assignments**: Assign cards to staff
- **Reading Info**: Create access logs for staff cards
- **Events**: Link events to reservations (especially meeting space reservations)
- **Customer Requests**: Create some open and resolved requests
- **Adjacency**: Define adjacent rooms (especially for meeting spaces)

---

## Step 8: Normalization Verification

Ensure all tables are in **3NF**:

1. **1NF**: All attributes are atomic (no repeating groups)
2. **2NF**: All non-key attributes fully depend on the primary key
3. **3NF**: No transitive dependencies (non-key attributes don't depend on other non-key attributes)

**Common Issues to Avoid:**
- Don't store calculated fields (like `days` in reservation) unless necessary for performance
- Don't duplicate customer information in reservation table
- Separate lookup tables (room_type, room_status) from entity tables
- Use foreign keys to maintain referential integrity

---

## Step 9: Indexes for Transactional Performance

Add indexes on frequently queried columns:

```sql
-- Already included in table definitions above
-- Additional indexes if needed:
CREATE INDEX idx_reservation_status ON reservation(status);
CREATE INDEX idx_room_status ON room(roomStatusId);
CREATE INDEX idx_customer_requests_resolved ON customer_requests(resolved, depositStatus);
```

---

## Step 10: Constraints and Data Integrity

Ensure all constraints are in place:
- Primary keys on all tables
- Foreign keys with appropriate ON DELETE actions
- CHECK constraints for data validation
- UNIQUE constraints where appropriate
- NOT NULL constraints on required fields

---

## Step 11: Testing Your Database

### Test Queries:

1. **Verify data counts:**
```sql
SELECT COUNT(*) as customer_count FROM customer;
SELECT COUNT(*) as reservation_count FROM reservation;
SELECT MIN(startDateTime) as earliest_date, MAX(endDateTime) as latest_date 
FROM reservation;
```

2. **Verify date span (must be at least one quarter):**
```sql
SELECT 
    DATEDIFF(MAX(endDateTime), MIN(startDateTime)) as days_span,
    DATEDIFF(MAX(endDateTime), MIN(startDateTime)) / 30.0 as months_span
FROM reservation;
-- Should be >= 90 days (3 months)
```

3. **Test referential integrity:**
```sql
-- Should return 0 rows (no orphaned reservations)
SELECT r.* FROM reservation r
LEFT JOIN customer c ON c.customerId = r.customerId
WHERE c.customerId IS NULL;
```

---

## Common Pitfalls to Avoid

1. **Insufficient Data**: Not meeting minimum customer/reservation counts
2. **Date Range Too Short**: Not spanning at least one quarter
3. **Normalization Issues**: Storing redundant data or violating 3NF
4. **Missing Foreign Keys**: Not enforcing referential integrity
5. **Inconsistent Data**: Dates that don't make sense, negative rates, etc.
6. **Missing Indexes**: Poor query performance for transactional use

---


---


