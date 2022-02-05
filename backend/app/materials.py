import datetime
import json
import random
import secrets
from functools import reduce
from pathlib import Path
from typing import List, Optional, Tuple, Dict

from PIL import Image, ImageDraw

from sqlalchemy import func
from sqlalchemy.orm import Session

from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi import Form, UploadFile, File

from . import exceptions
from .main import app, manager
from .db import models, get_db
from . import schemas
from . import utils


@app.post("/api/v1/product", description="Добавляем новую продукцию", tags=["products"])
async def add_new_product(
    # previous_id: Optional[int] = Form(None),
    update: bool = Form(...),
    article: int = Form(...),
    name: str = Form(...),
    price: float = Form(...),
    width: int = Form(...),
    length: int = Form(...),
    comment: str = Form(...),
    image: UploadFile = File(...),
    cloth_pieces: List[schemas.PiecesDescription] = Depends(
        schemas.PiecesDescription.from_json
    ),
    accessory_articles: str = Form(...),
    size: int = Form(...),
    user: models.User = Depends(manager),
    db: Session = Depends(get_db),
):
    if not update:
        same_article = (
            db.query(models.Product)
            .filter(models.Product.article == article)
            .one_or_none()
        )
        if same_article is not None:
            raise exceptions.ArticleAlreadyExists

    new_product: models.ProductWithPreviousAccessoryCloth = (
        models.ProductWithPreviousAccessoryCloth()
    )
    new_product.article = article
    new_product.name = name
    new_product.length = length
    new_product.width = width
    image_filename = await utils.save_file(image)
    new_product.image = image_filename
    new_product.comment = comment
    new_product.price = price
    new_product.size = size
    db.add(new_product)
    db.flush()
    db.refresh(new_product)
    if update:
        prev: models.Product = (
            db.query(models.Product)
            .filter(
                models.Product.current_active == True,
                models.Product.article == article,
                models.Product.id != new_product.id,
                models.Product.size == size,
            )
            .one_or_none()
        )
        if prev is None:
            raise exceptions.ArticleDoesNotExist
        prev.current_active = False
        print("prev.id = ", prev.id)
        prev.next_id = new_product.id
        prev.changed_date = datetime.datetime.now()
    db.flush()
    db.refresh(new_product)

    # for cloth in cloth_articles:
    #
    #     db.execute(
    #         models.ProductClothRelations.insert().values(
    #             product_id=new_product.id, cloth_article=cloth
    #         )
    #     )
    #
    # for accessory in accessory_articles:
    #     db.execute(
    #         models.ProductAccessoryRelations.insert().values(
    #             product_id=new_product.id, accessory_article=accessory
    #         )
    #     )

    accessory_articles = json.loads(
        accessory_articles if accessory_articles != "" else "[]"
    )

    for accessory in accessory_articles:
        new_product.accessories.append(
            db.query(models.Accessory).filter(models.Accessory.article == accessory)
        )

    for cloth_object in cloth_pieces:
        cloth: models.Cloth = (
            db.query(models.Cloth)
            .filter(models.Cloth.article == cloth_object.article)
            .one()
        )
        if cloth not in new_product.clothes:
            new_product.clothes.append(cloth)
        new_piece: models.ClothPiece = models.ClothPiece()
        new_piece.width = cloth_object.width
        new_piece.length = cloth_object.length
        new_piece.cloth_article = cloth.article
        new_piece.product_id = new_product.id
        new_piece.count = cloth_object.count

        db.add(new_piece)

    db.commit()
    db.flush()

    return JSONResponse(
        status_code=200, content={"description": "Product created successfully"}
    )


@app.get(
    "/api/v1/product",
    response_model=List[schemas.Product],
    response_model_exclude={"previous"},
    tags=["products"],
)
async def get_products(db: Session = Depends(get_db)):
    return (
        db.query(models.ProductWithPreviousAccessoryCloth)
        .filter(models.ProductWithPreviousAccessoryCloth.current_active == True)
        .all()
    )


@app.get(
    "/api/v1/product/{article}",
    response_model=Optional[schemas.Product],
    response_model_exclude={"previous"},
    tags=["products"],
    deprecated=True,
)
async def get_product_by_article(article: int, db: Session = Depends(get_db)):
    return (
        db.query(models.ProductWithPreviousAccessoryCloth)
        .filter(
            models.ProductWithPreviousAccessoryCloth.current_active == True,
            models.ProductWithPreviousAccessoryCloth.article == article,
        )
        .one_or_none()
    )


@app.get(
    "/api/v1/product/v2/{article}/{size}",
    response_model=Optional[schemas.Product],
    response_model_exclude={"previous"},
    tags=["products"],
)
async def get_product_by_article_and_size(
    article: int, size: int, db: Session = Depends(get_db)
):
    return (
        db.query(models.ProductWithPreviousAccessoryCloth)
        .filter(
            models.ProductWithPreviousAccessoryCloth.current_active == True,
            models.ProductWithPreviousAccessoryCloth.article == article,
            models.ProductWithPreviousAccessoryCloth.size == size,
        )
        .one_or_none()
    )


@app.get(
    "/api/v1/product/{article}/previous",
    response_model=List[schemas.Product],
    response_model_exclude={"previous"},
    tags=["products"],
    deprecated=True,
)
async def get_parents_by_article(article: int, db: Session = Depends(get_db)):
    answer: List[models.ProductWithPreviousAccessoryCloth] = [
        db.query(models.ProductWithPreviousAccessoryCloth)
        .filter(
            models.ProductWithPreviousAccessoryCloth.article == article,
            models.ProductWithPreviousAccessoryCloth.current_active == True,
        )
        .one_or_none()
    ]
    if answer[0] is None:
        raise exceptions.ArticleDoesNotExist

    exists = True

    while exists:
        new_parent = (
            db.query(models.ProductWithPreviousAccessoryCloth)
            .filter(
                models.ProductWithPreviousAccessoryCloth.article == article,
                models.ProductWithPreviousAccessoryCloth.next_id
                == answer[len(answer) - 1].id,
            )
            .one_or_none()
        )
        if new_parent is None:
            exists = False
            continue
        answer.append(new_parent)

    answer = answer[1:]

    return answer


@app.get(
    "/api/v1/product/v2/{article}/{size}/previous",
    response_model=List[schemas.Product],
    response_model_exclude={"previous"},
    tags=["products"],
)
async def get_parents_by_article(
    article: int, size: int, db: Session = Depends(get_db)
):
    answer: List[models.ProductWithPreviousAccessoryCloth] = [
        db.query(models.ProductWithPreviousAccessoryCloth)
        .filter(
            models.ProductWithPreviousAccessoryCloth.article == article,
            models.ProductWithPreviousAccessoryCloth.current_active == True,
            models.ProductWithPreviousAccessoryCloth.size == size,
        )
        .one_or_none()
    ]
    if answer[0] is None:
        raise exceptions.ArticleDoesNotExist

    exists = True

    while exists:
        new_parent = (
            db.query(models.ProductWithPreviousAccessoryCloth)
            .filter(
                models.ProductWithPreviousAccessoryCloth.article == article,
                models.ProductWithPreviousAccessoryCloth.next_id
                == answer[len(answer) - 1].id,
                models.ProductWithPreviousAccessoryCloth.size == size,
            )
            .one_or_none()
        )
        if new_parent is None:
            exists = False
            continue
        answer.append(new_parent)

    answer = answer[1:]

    return answer


@app.get("/api/v1/get_cloth_mappings/{order_id}")
async def get_cloth_mapping(
    order_id: int, user: models.User = Depends(manager), db: Session = Depends(get_db)
):
    if user.role not in [
        models.UserType.chef,
        models.UserType.manager,
        models.UserType.former_employee,
    ]:
        raise exceptions.InsufficientPrivileges

    order: models.OrderWithAllInfo = (
        db.query(models.OrderWithAllInfo)
        .filter(models.OrderWithAllInfo.id == order_id)
        .one_or_none()
    )

    if order is None:
        raise exceptions.OrderDoesNotExist

    cloth_pieces = {}
    for product in order.products:
        cp: List[models.ClothPiece] = (
            db.query(models.ClothPiece)
            .filter(models.ClothPiece.product_id == product.product.id)
            .all()
        )
        for piece in cp:
            if piece.cloth_article not in cloth_pieces.keys():
                cloth_pieces[piece.cloth_article] = []
            for _ in range(piece.count):
                if piece.width < piece.length:
                    cloth_pieces[piece.cloth_article].append(
                        (int(float(piece.length * 100)), int(float(piece.width) * 100))
                    )
                else:
                    cloth_pieces[piece.cloth_article].append(
                        (int(float(piece.width) * 100), int(float(piece.length * 100)))
                    )

    answer = []
    for key, item in cloth_pieces.items():
        answer.append(get_current_mapping(key, item, db))
        if None in answer:
            return JSONResponse(
                status_code=404,
                content={
                    "detail": "Ткани не хватает"
                }
            )

    return answer


def get_current_mapping(article: int, pieces: List[Tuple[int, int]], db: Session) -> Optional[Dict]:
    batches: List[models.ClothStorage] = (
        db.query(models.ClothStorage)
        .filter(models.ClothStorage.article == article)
        .order_by(models.ClothStorage.length.desc())
        .all()
    )

    pieces = sorted(pieces, key=lambda e:(-e[0], -e[1]))

    cloth_width = int(float(db.query(models.Cloth.width).filter(models.Cloth.article == article).one().width)*100)

    max_height = reduce(lambda x, y: (x[0]+y[0], x[1]+y[1]), pieces)[0]
    batch = [[-1 for i in range(cloth_width)] for _ in range(max_height)]

    current_floor = 0
    current_ceil = -1
    current_x = 0

    piece_number = 0
    floor_fulling = True

    while len(pieces) > 0:
        print(pieces)
        if current_ceil < current_floor:
            current_ceil = current_floor+pieces[0][0]
            for i in range(current_floor, current_floor+pieces[0][0]):
                for j in range(current_x, current_x+pieces[0][1]):
                    batch[i][j] = piece_number
            piece_number += 1
            current_x = pieces[0][1]
            if current_x >= cloth_width:
                current_x = cloth_width-1
                floor_fulling = not floor_fulling
            pieces = pieces[1:]
            print("added to new floor")
            continue
        if floor_fulling:
            element_found = False
            for i in range(len(pieces)):
                if pieces[i][1]+current_x <= cloth_width:
                    for j in range(current_floor, current_floor + pieces[i][0]):
                        for k in range(current_x, current_x + pieces[i][1]):
                            batch[j][k] = piece_number

                    current_x += pieces[i][1]
                    piece_number += 1
                    element_found = True
                    pieces = pieces[:i]+pieces[i+1:]
                    print("added to floor")
                    break
            if not element_found:
                current_x = cloth_width - 1
                floor_fulling = not floor_fulling

        else:
            rotated_figures = [(e[1], e[0]) for e in pieces]
            element_found = False

            for i in range(len(pieces)):
                is_free = True
                if current_ceil - 1 - pieces[i][0]<-1 or current_x - pieces[i][1]<-1:
                    is_free = False
                else:
                    for j in range(current_ceil-1, current_ceil-1-pieces[i][0], -1):
                        for k in range(current_x, current_x-pieces[i][1], -1):
                            if batch[j][k] != -1:
                                is_free = False

                if is_free:
                    for j in range(current_ceil - 1, current_ceil - 1 - pieces[i][0], -1):
                        for k in range(current_x, current_x - pieces[i][1], -1):
                            batch[j][k] = piece_number
                    element_found = True
                    current_x -= pieces[i][1]
                    piece_number+=1
                    pieces = pieces[:i] + pieces[i+1:]
                    rotated_figures = rotated_figures[:i] + rotated_figures[i+1:]
                    print("added to ceil")
                    break
            if element_found:
                continue

            for i in range(len(rotated_figures)):
                is_free = True
                if current_ceil - 1 - rotated_figures[i][0] < -1 or current_x - rotated_figures[i][1] < -1:
                    is_free = False
                else:
                    for j in range(current_ceil - 1, current_ceil - 1 - rotated_figures[i][0], -1):
                        for k in range(current_x, current_x - rotated_figures[i][1], -1):
                            if batch[j][k] != -1:
                                is_free = False


                if is_free:
                    for j in range(current_ceil - 1, current_ceil - 1 - rotated_figures[i][0], -1):
                        for k in range(current_x, current_x - rotated_figures[i][1], -1):
                            batch[j][k] = piece_number
                    element_found = True
                    pieces = pieces[:i] + pieces[i + 1:]
                    rotated_figures = rotated_figures[:i] + rotated_figures[i + 1:]
                    current_x -= rotated_figures[i][1]
                    piece_number+=1
                    print("added to rotated")
                    break

            if not element_found:
                floor_fulling = True
                current_floor = current_ceil
                current_ceil = current_floor-1
                current_x = 0

    img = Image.new('RGB', (cloth_width, current_ceil), 'white')
    draw = ImageDraw.Draw(img)
    colors = []
    for i in range(piece_number):
        colors.append(
            (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        )
    for i in range(current_ceil):
        for j in range(cloth_width):
            if batch[i][j] != -1:
                draw.point((j, img.size[1]-i), colors[batch[i][j]])

    name = secrets.token_hex(32)
    img.save(Path().parent/"static"/f"{name}.jpg")
    answer = {
        "article": article,
        "map": f"static/{name}.jpg",
        "batch_number": -1,
    }
    for batch in batches:
        if float(batch.length)>=current_ceil/100:
            answer["batch_number"] = batch.number

    return answer if answer["batch_number"] != -1 else None