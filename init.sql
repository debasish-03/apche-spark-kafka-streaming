CREATE TABLE products (
    userid INT,
    productid INT,
    source TEXT,
    timestamp TIMESTAMP
);


CREATE TABLE orders (
    orderid VARCHAR(255),
    userid INTEGER,
    productid INTEGER,
    quantity INTEGER,
    timestamp TIMESTAMP
);
