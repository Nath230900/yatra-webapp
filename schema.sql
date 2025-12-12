-- DROP TABLES IF THEY ALREADY EXIST (SAFE RESET)
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS itinerary_items;
DROP TABLE IF EXISTS itineraries;
DROP TABLE IF EXISTS destinations;
DROP TABLE IF EXISTS users;

-- USERS TABLE
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_admin INTEGER DEFAULT 0, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DESTINATIONS TABLE
CREATE TABLE destinations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(150) NOT NULL,
    region VARCHAR(100),
    category VARCHAR(100),
    description TEXT,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    image_url VARCHAR(255),
    highlights TEXT
);
--DESTINATIONS IMAGES TABLE
CREATE TABLE destination_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    destination_id INTEGER NOT NULL,
    filename VARCHAR(255) NOT NULL,
    is_primary INTEGER DEFAULT 0,
    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE
);


-- ITINERARIES TABLE
CREATE TABLE itineraries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(150) NOT NULL,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ITINERARY ITEMS TABLE
CREATE TABLE itinerary_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    itinerary_id INTEGER NOT NULL,
    day_number INTEGER NOT NULL,
    destination_id INTEGER NOT NULL,
    notes TEXT,
    FOREIGN KEY (itinerary_id) REFERENCES itineraries(id) ON DELETE CASCADE,
    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE
);

-- REVIEWS TABLE
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    destination_id INTEGER NOT NULL,
    rating INTEGER,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE
);


INSERT INTO destinations
(name, region, category, description, latitude, longitude, image_url, highlights)
VALUES
('Kathmandu Durbar Square', 'Kathmandu Valley', 'Cultural Heritage',
 'UNESCO World Heritage Site with palaces, courtyards and temples dating back to the Malla period.',
 27.704590, 85.307600,
 'kathmandu.jpg',
 'Hanuman Dhoka Palace; Taleju Temple; Kumari Ghar'),

('Pashupatinath Temple', 'Kathmandu Valley', 'Religious / Cultural',
 'Sacred Hindu temple complex on the Bagmati River, major pilgrimage site.',
 27.710440, 85.348890,
 'pashupatinath.jpg',
 'Evening aarti; Bagmati ghats'),

('Boudhanath Stupa', 'Kathmandu Valley', 'Buddhist Heritage',
 'One of the largest spherical stupas in the world, Buddhist pilgrimage centre.',
 27.721390, 85.362000,
 'boudhanath.jpg',
 'Monastery circuit walk; prayer wheels'),

('Pokhara Lakeside & Phewa Lake', 'Gandaki Province', 'Nature & Leisure',
 'Lakeside city with stunning views of the Annapurna range and relaxed atmosphere.',
 28.209600, 83.985600,
 'pokhara.jpg',
 'Boating; World Peace Pagoda; sunrise at Sarangkot'),

('Chitwan National Park', 'Bagmati Province', 'Wildlife / Safari',
 'UNESCO-listed national park famous for one-horned rhino, Bengal tigers and jungle safaris.',
 27.534200, 84.461000,
 'chitwan.jpg',
 'Jeep safari; canoeing; Tharu cultural program'),

('Lumbini – Birthplace of Buddha', 'Lumbini Province', 'Religious / Heritage',
 'Sacred site where Siddhartha Gautama was born; monasteries from Buddhist communities worldwide.',
 27.476300, 83.276000,
 'LUMBINI.jpg',
 'Maya Devi Temple; sacred pond; monastic zone'),

('Bhaktapur Durbar Square', 'Kathmandu Valley', 'Cultural Heritage',
 'Medieval Newari city with beautifully preserved architecture and traditional lifestyle.',
 27.672900, 85.429800,
 'bhaktapur.jpg',
 '55-Window Palace; Nyatapola Temple; pottery square'),

('Langtang National Park', 'Bagmati Province', 'Trekking / Nature',
 'Himalayan valley famous for trekking, Tamang culture and alpine scenery north of Kathmandu.',
 28.211000, 85.500000,
 'langtang.jpg',
 'Langtang Valley Trek; Kyanjin Gompa; yak pastures');
 
 --DESTINATION IMAGES INSERTIONS
 INSERT INTO destination_images (destination_id, filename, is_primary) VALUES
(1, 'kathmandu.jpg', 1),
(2, 'pashupatinath.jpg', 1),
(3, 'boudha.jpg', 1),
(4, 'pokhara.jpg', 1),
(5, 'chitwan.jpg', 1),
(6, 'LUMBINI.jpg', 1),
(7, 'bhaktapur.jpg', 1);

