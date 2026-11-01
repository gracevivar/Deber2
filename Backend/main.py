from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, create_engine, Session, select

# Modelo de la base de datos
class Producto(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    descripcion: str
    precio: float
    imagen: str | None = None
    stock: int = 0


# Esquemas de la API
class ProductoCreate(SQLModel):
    nombre: str
    descripcion: str
    precio: float
    imagen: str | None = None
    stock: int = 0

class ProductoRead(SQLModel):
    id: int
    nombre: str
    descripcion: str
    precio: float
    imagen: str | None = None
    stock: int = 0


sqlite_url = "sqlite:///productos.db"
engine = create_engine(sqlite_url, echo=True)

def create_tables():
    SQLModel.metadata.create_all(engine)

app = FastAPI(lifespan=create_tables())

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"]
)

@app.get("/")
def read_root():
    return {"message": "API de productos"}


@app.post("/productos", status_code=status.HTTP_201_CREATED, response_model=ProductoRead)
def create_producto(datos: ProductoCreate):
    producto = Producto(nombre=datos.nombre, descripcion=datos.descripcion, precio=datos.precio, imagen=datos.imagen, stock=datos.stock)
    with Session(engine) as session:
        session.add(producto)
        session.commit()
        session.refresh(producto)
        return producto

@app.get("/productos", response_model=list[ProductoRead])
def read_productos():
    with Session(engine) as session:
        return session.exec(select(Producto)).all()

@app.get("/productos/{producto_id}", response_model=ProductoRead)
def read_producto(producto_id: int):
    with Session(engine) as session:
        producto = session.get(Producto, producto_id)
        if producto is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
        return producto

@app.delete("/productos/{producto_id}")
def delete_producto(producto_id: int):
    with Session(engine) as session:
        producto = session.get(Producto, producto_id)
        if producto is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
        session.delete(producto)
        session.commit()
        return {"message": "Producto eliminado exitosamente"}


