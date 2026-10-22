# File Upload & Download API

A FastAPI backend for uploading, validating, listing, downloading and deleting product images and supplier PDF documents.

## Features

- JPG, JPEG and PNG product images.
- PDF supplier documents.
- Maximum file size of 5 MiB (5,242,880 bytes).
- Extension, MIME type and file-content validation.
- UUID-based stored filenames.
- Separate folders for product images and supplier documents.
- File metadata stored in SQLAlchemy/MySQL.
- JWT-protected endpoints and per-user ownership checks.
- Product-to-image association.
- Alembic migration and Postman collection.

## Project setup

Activate the virtual environment in PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1