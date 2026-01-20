# CRUD Modules Implementation Documentation

## Overview
This document describes the implementation of 4 new CRUD modules added to the Defect Detection System:
1. Customer Management
2. Product Management
3. Defect Type Management
4. Severity Level Management

## Files Changed/Added

### Backend Files

#### Models (`backend/app/models/`)
- **customer.py** - Customer model with unique customer_code constraint
- **product.py** - Product model with foreign key to Customer
- **defect_type.py** - DefectType catalog model
- **severity_level.py** - SeverityLevel catalog model
- **__init__.py** - Updated to export new models

#### Schemas (`backend/app/schemas/`)
- **customer.py** - CustomerCreate, CustomerUpdate, CustomerResponse schemas
- **product.py** - ProductCreate, ProductUpdate, ProductResponse schemas
- **defect_type.py** - DefectTypeCreate, DefectTypeUpdate, DefectTypeResponse schemas
- **severity_level.py** - SeverityLevelCreate, SeverityLevelUpdate, SeverityLevelResponse schemas

#### API Endpoints (`backend/app/api/endpoints/`)
- **customers.py** - Customer CRUD endpoints
- **products.py** - Product CRUD endpoints
- **defect_types.py** - DefectType CRUD endpoints
- **severity_levels.py** - SeverityLevel CRUD endpoints

#### Core Files
- **main.py** - Updated to register new routers with `/api` prefix

### Frontend Files

#### Pages (`frontend/src/pages/`)
- **CustomerManagement.jsx** - Customer CRUD UI
- **ProductManagement.jsx** - Product CRUD UI with customer dropdown
- **DefectTypeManagement.jsx** - DefectType CRUD UI with bilingual display
- **SeverityLevelManagement.jsx** - SeverityLevel CRUD UI with bilingual display

#### Services
- **api.js** - Added customerAPI, productAPI, defectTypeAPI, severityLevelAPI

#### Routing and Navigation
- **App.jsx** - Added routes for 4 new pages
- **Layout.jsx** - Added 4 new admin-only menu items with icons

#### Configuration
- **nginx.conf** - Fixed to preserve `/api` prefix in proxy

## API Endpoints

### Customer Endpoints
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/customers/ | List all customers with search | Admin |
| GET | /api/customers/{id} | Get customer by ID | Admin |
| POST | /api/customers/ | Create new customer | Admin |
| PUT | /api/customers/{id} | Update customer | Admin |
| DELETE | /api/customers/{id} | Delete customer | Admin |

**Request Body (Create/Update):**
```json
{
  "customer_code": "CUST001",
  "customer_name": "Customer Name"
}
```

**Response:**
```json
{
  "id": 1,
  "customer_code": "CUST001",
  "customer_name": "Customer Name",
  "created_at": "2026-01-20T00:00:00Z",
  "updated_at": null
}
```

### Product Endpoints
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/products/ | List all products with search | Admin |
| GET | /api/products/{id} | Get product by ID | Admin |
| POST | /api/products/ | Create new product | Admin |
| PUT | /api/products/{id} | Update product | Admin |
| DELETE | /api/products/{id} | Delete product | Admin |

**Request Body (Create/Update):**
```json
{
  "product_code": "PROD001",
  "product_name": "Product Name",
  "customer_id": 1
}
```

**Response:**
```json
{
  "id": 1,
  "product_code": "PROD001",
  "product_name": "Product Name",
  "customer_id": 1,
  "customer": {
    "id": 1,
    "customer_code": "CUST001",
    "customer_name": "Customer Name"
  },
  "created_at": "2026-01-20T00:00:00Z",
  "updated_at": null
}
```

### Defect Type Endpoints
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/defect-types/ | List all defect types with search | Admin |
| GET | /api/defect-types/{id} | Get defect type by ID | Admin |
| POST | /api/defect-types/ | Create new defect type | Admin |
| PUT | /api/defect-types/{id} | Update defect type | Admin |
| DELETE | /api/defect-types/{id} | Delete defect type | Admin |

**Request Body (Create/Update):**
```json
{
  "defect_code": "CRACK",
  "name_vi": "Nứt",
  "name_en": "Crack"
}
```

**Response:**
```json
{
  "id": 1,
  "defect_code": "CRACK",
  "name_vi": "Nứt",
  "name_en": "Crack",
  "display_name": "Nứt (Crack)",
  "created_at": "2026-01-20T00:00:00Z",
  "updated_at": null
}
```

### Severity Level Endpoints
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/severity-levels/ | List all severity levels with search | Admin |
| GET | /api/severity-levels/{id} | Get severity level by ID | Admin |
| POST | /api/severity-levels/ | Create new severity level | Admin |
| PUT | /api/severity-levels/{id} | Update severity level | Admin |
| DELETE | /api/severity-levels/{id} | Delete severity level | Admin |

**Request Body (Create/Update):**
```json
{
  "severity_code": "CRITICAL",
  "name_vi": "Nghiêm trọng",
  "name_en": "Critical"
}
```

**Response:**
```json
{
  "id": 1,
  "severity_code": "CRITICAL",
  "name_vi": "Nghiêm trọng",
  "name_en": "Critical",
  "display_name": "Nghiêm trọng (Critical)",
  "created_at": "2026-01-20T00:00:00Z",
  "updated_at": null
}
```

## Testing with curl

### 1. Login to get JWT token
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# Save the token from response
TOKEN="<your_jwt_token>"
```

### 2. Create a Customer
```bash
curl -X POST http://localhost:8000/api/customers/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"customer_code":"CUST001","customer_name":"ABC Company"}'
```

### 3. List Customers
```bash
curl -X GET http://localhost:8000/api/customers/ \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Create a Product
```bash
curl -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_code":"PROD001","product_name":"Widget A","customer_id":1}'
```

### 5. List Products
```bash
curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Bearer $TOKEN"
```

### 6. Create a Defect Type
```bash
curl -X POST http://localhost:8000/api/defect-types/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"defect_code":"CRACK","name_vi":"Nứt","name_en":"Crack"}'
```

### 7. Create a Severity Level
```bash
curl -X POST http://localhost:8000/api/severity-levels/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"severity_code":"CRITICAL","name_vi":"Nghiêm trọng","name_en":"Critical"}'
```

### 8. Test Customer Deletion Protection
```bash
# This should fail with error message about linked products
curl -X DELETE http://localhost:8000/api/customers/1 \
  -H "Authorization: Bearer $TOKEN"
```

### 9. Delete Product First, Then Customer
```bash
# Delete the product
curl -X DELETE http://localhost:8000/api/products/1 \
  -H "Authorization: Bearer $TOKEN"

# Now delete customer (should succeed)
curl -X DELETE http://localhost:8000/api/customers/1 \
  -H "Authorization: Bearer $TOKEN"
```

## UI Flow

### Customer Management
1. Navigate to sidebar menu "Khách Hàng" (admin only)
2. View list of customers in table format
3. Click "Thêm Khách Hàng" to open create dialog
4. Fill in customer_code and customer_name
5. Click "Tạo mới" to create
6. Use Edit icon to update existing customers
7. Use Delete icon to remove customers (blocked if products exist)

### Product Management
1. Navigate to sidebar menu "Sản Phẩm" (admin only)
2. View list of products with linked customer info
3. Click "Thêm Sản Phẩm" to open create dialog
4. Fill in product_code, product_name, and select customer from dropdown
5. Click "Tạo mới" to create
6. Customer info displayed as chip showing "customer_name (customer_code)"
7. Use Edit/Delete icons for modifications

### Defect Type Management
1. Navigate to sidebar menu "Loại Lỗi" (admin only)
2. View list showing bilingual display format "name_vi (name_en)"
3. Click "Thêm Loại Lỗi" to create new type
4. Fill in defect_code, name_vi, and name_en
5. Display format automatically shown as "name_vi (name_en)"

### Severity Level Management
1. Navigate to sidebar menu "Mức Độ" (admin only)
2. View list showing bilingual display format "name_vi (name_en)"
3. Click "Thêm Mức Độ" to create new level
4. Fill in severity_code, name_vi, and name_en
5. Display format automatically shown as "name_vi (name_en)"

## Key Features Implemented

### Backend Features
1. **Unique Constraints** - customer_code, product_code, defect_code, severity_code are all unique
2. **Foreign Key Protection** - Product has RESTRICT on delete for customer_id
3. **Cascade Delete Prevention** - Cannot delete customer with linked products
4. **Search Functionality** - All endpoints support search by code or name
5. **Pagination** - skip/limit parameters for list endpoints
6. **Computed Fields** - display_name field computed in Pydantic response schemas
7. **Admin-Only Access** - All endpoints require admin role
8. **Timestamps** - created_at and updated_at tracked automatically

### Frontend Features
1. **Consistent UI Pattern** - All pages follow Material-UI design
2. **Dialog-Based Forms** - Create/Edit using Dialog components
3. **Toast Notifications** - Success/error feedback with react-toastify
4. **Icon Integration** - Material icons for visual clarity
5. **Bilingual Display** - DefectType and SeverityLevel show both languages
6. **Related Data Display** - Product shows linked customer information
7. **Delete Confirmation** - window.confirm() before deletion
8. **Loading States** - CircularProgress during data fetching
9. **Error Handling** - Alert components for error messages
10. **Admin-Only Routes** - Menu items hidden for non-admin users

## Database Schema

### customers table
```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    customer_code VARCHAR(50) UNIQUE NOT NULL,
    customer_name VARCHAR(200) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX idx_customers_code ON customers(customer_code);
```

### products table
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    product_code VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX idx_products_code ON products(product_code);
CREATE INDEX idx_products_customer ON products(customer_id);
```

### defect_types table
```sql
CREATE TABLE defect_types (
    id SERIAL PRIMARY KEY,
    defect_code VARCHAR(50) UNIQUE NOT NULL,
    name_vi VARCHAR(200) NOT NULL,
    name_en VARCHAR(200) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX idx_defect_types_code ON defect_types(defect_code);
```

### severity_levels table
```sql
CREATE TABLE severity_levels (
    id SERIAL PRIMARY KEY,
    severity_code VARCHAR(50) UNIQUE NOT NULL,
    name_vi VARCHAR(200) NOT NULL,
    name_en VARCHAR(200) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX idx_severity_levels_code ON severity_levels(severity_code);
```

## Error Handling

### Common Error Responses

**400 Bad Request** - Duplicate code or validation error
```json
{
  "detail": "Customer code 'CUST001' already exists"
}
```

**404 Not Found** - Resource not found
```json
{
  "detail": "Customer not found"
}
```

**400 Bad Request** - Delete customer with products
```json
{
  "detail": "Cannot delete customer. 3 product(s) are linked to this customer."
}
```

**401 Unauthorized** - Missing or invalid JWT token
```json
{
  "detail": "Not authenticated"
}
```

**403 Forbidden** - Non-admin user accessing admin endpoint
```json
{
  "detail": "Admin access required"
}
```

## Deployment Steps

1. **Rebuild Docker containers**
   ```bash
   ./rebuild.sh
   ```

2. **Verify services are running**
   ```bash
   docker compose ps
   ```

3. **Check backend logs**
   ```bash
   docker compose logs backend
   ```

4. **Access frontend**
   - Open browser to http://localhost:3002
   - Login with admin credentials
   - Navigate to new modules in sidebar

5. **Test database tables**
   ```bash
   docker compose exec db psql -U postgres -d defect_system -c "\dt"
   ```

## Future Enhancements

1. **Bulk Operations** - Import/export customers and products via CSV
2. **Audit Logging** - Track who created/modified records
3. **Soft Delete** - Archive instead of permanently deleting
4. **Advanced Search** - Filter by multiple criteria
5. **Sorting** - Client-side table sorting
6. **Validation** - Client-side form validation with error messages
7. **Internationalization** - Full i18n support for Vietnamese/English
8. **Product History** - Track product changes over time
9. **Customer Dashboard** - Summary statistics per customer
10. **API Rate Limiting** - Prevent abuse of endpoints
