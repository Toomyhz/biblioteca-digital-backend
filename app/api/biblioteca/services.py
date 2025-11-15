from flask import request
from sqlalchemy import func,or_
from app.models.libros import Libros
from app.models.autores import Autores
from app.models.carreras import Carreras
from app import db
def listar_libros_biblioteca():
    try:
        # ----- Parámetros -----
        pagina = request.args.get("pagina",1,type=int)
        limite = request.args.get("limite",10,type=int)
        busqueda = request.args.get("busqueda","",type=str)
        carreras_filtro = request.args.get("carrera","",type=str).split(",") if request.args.get("carrera") else []
        autores_filtro = request.args.get("autor","",type=str).split(",") if request.args.get("autor") else []
        
        query = Libros.query

        # ---- Filtros -----
        if busqueda:
            busqueda_normalizada = busqueda.strip().lower()
            busqueda_patron = f"%{busqueda_normalizada}%"
            query = query.filter(
                or_(
                    # Buscar en titulo
                    func.lower(Libros.titulo).like(busqueda_patron),
                    # Buscar en ISBN
                    func.lower(Libros.isbn).like(busqueda_patron),
                    #Buscar en año
                    func.lower(Libros.anio_publicacion).like(busqueda_patron),

                    # Buscar en autores relacionados
                    Libros.autores.any(
                        func.lower(Autores.nombre_completo).like(busqueda_patron)
                    ),

                    # Buscar en carreras relacionadas
                    Libros.carreras.any(
                        func.lower(Carreras.nombre_carrera).like(busqueda_patron)
                    )
            ))
        
        if carreras_filtro:
            query = query.filter(
                Libros.carreras.any(Carreras.id_carrera.in_(carreras_filtro))
            )
        

        if autores_filtro:
            query = query.filter(
                Libros.autores.any(Autores.id_autor.in_(autores_filtro))
            )

        #  ---- Paginacion -----
        paginacion = query.order_by(Libros.id_libro.desc()).paginate(
            page = pagina, per_page=limite, error_out=False
        )

        libros = [libro.to_dict() for libro in paginacion.items]
         # ----- Carreras visibles (máximo 7) -----
        carreras_visibles = (
            db.session.query(
                Carreras.id_carrera,
                Carreras.nombre_carrera,
                func.count(Libros.id_libro).label("total_libros")
            )
            .join(Carreras.libros)
            .group_by(Carreras.id_carrera, Carreras.nombre_carrera)
            .order_by(func.count(Libros.id_libro).desc())
            .limit(7)
            .all()
        )
        carreras_data = [
            {"id_carrera": c[0], "nombre_carrera": c[1], "total_libros": c[2]}
            for c in carreras_visibles
        ]

        # ----- Autores visibles (máximo 7) -----
        subquery_ids_query = query.with_entities(Libros.id_libro)

        autores_visibles = (
            db.session.query(
                Autores.id_autor,
                Autores.nombre_completo,
                func.count(Libros.id_libro).label("total_libros")
            )
            .join(Autores.libros)
            .filter(Libros.id_libro.in_(subquery_ids_query.scalar_subquery()))
            .group_by(Autores.id_autor, Autores.nombre_completo)
            .order_by(func.count(Libros.id_libro).desc())
            .limit(7)
            .all()
        )

        autores_data = [
            {"id_autor": a[0], "nombre_completo": a[1], "total_libros": a[2]}
            for a in autores_visibles
        ]

        # ----- Respuesta -----
        return {
            "libros": {
                "data": libros,
                "paginacion": {
                    "pagina": paginacion.page,
                    "limite": paginacion.per_page,
                    "total": paginacion.total,
                    "total_paginas": paginacion.pages,
                },
            },
            "carreras": {
                "visibles": carreras_data,
                "total": db.session.query(func.count(Carreras.id_carrera)).scalar()
            },
            "autores": {
                "visibles": autores_data,
                "total": db.session.query(func.count(Autores.id_autor)).scalar()
            }
        }, 200
    
    except Exception as e:
        db.session.rollback()
        return {'error': f'Error al listar libros: {str(e)}'}, 500