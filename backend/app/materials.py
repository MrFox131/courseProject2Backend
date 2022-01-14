import json
import math
import secrets
from pathlib import Path
from typing import List, Optional, Dict

from borb.pdf.canvas.layout.layout_element import Alignment
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi import Form, UploadFile, File

from . import exceptions
from .main import app, manager
from .db import models, get_db
from . import schemas
from . import utils

from decimal import Decimal

from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.page_layout.page_layout import PageLayout
from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.document import Document
from borb.pdf.page.page import Page
from borb.pdf.pdf import PDF
from borb.pdf.canvas.font.simple_font.true_type_font import TrueTypeFont
from borb.pdf.canvas.font.font import Font


@app.get("/api/v1/cloth", response_model=List[schemas.Cloth], tags=["storage"])
async def get_clothes(
    user: models.User = Depends(manager), db: Session = Depends(get_db)
):
    return db.query(models.Cloth).all()


@app.get("/api/v1/accessory", response_model=List[schemas.Accessory], tags=["storage"])
async def get_accessories(
    user: models.User = Depends(manager), db: Session = Depends(get_db)
):
    return db.query(models.Accessory).all()


@app.get("/api/v1/accessory_by_id/{article}", response_model=schemas.Accessory, tags=["storage"])
async def get_accessories(
        article: int,
        user: models.User = Depends(manager), db: Session = Depends(get_db)
):
    return db.query(models.Accessory).filter(models.Accessory.article == article).one()


@app.get("/api/v1/cloth_by_id/{article}")
async def cloth_by_article(
        article: int, user: models.User = Depends(manager), db: Session = Depends(get_db)
):
    return db.query(models.Cloth).filter(models.Cloth.article == article).one()


@app.get(
    "/api/v1/cloth/{article}",
    response_model=List[schemas.ClothStorage],
    tags=["storage"],
)
async def get_cloth_packs(
    article: int, user: models.User = Depends(manager), db: Session = Depends(get_db)
):
    return (
        db.query(models.ClothStorage)
        .filter(models.ClothStorage.article == article)
        .all()
    )


@app.get(
    "/api/v1/accessory/{article}",
    response_model=Optional[schemas.AccessoryStorage],
    tags=["storage"],
)
async def get_accessory_packs(
    article: int, user: models.User = Depends(manager), db: Session = Depends(get_db)
):
    accessory = (
        db.query(models.AccessoriesStorage)
        .filter(models.AccessoriesStorage.article == article)
        .one_or_none()
    )

    return accessory


@app.get(
    "/api/v1/accessory_with_info/{article}",
    response_model=Optional[schemas.AccessoryStorageWithAccessory],
    tags=["storage"],
)
async def get_accessory_with_info_packs(
        article: int, user: models.User = Depends(manager), db: Session = Depends(get_db)
):
    accessory = (
        db.query(models.AccessoriesStorageWithAccessory)
            .filter(models.AccessoriesStorage.article == article)
            .one_or_none()
    )

    return accessory


@app.post(
    "/api/v1/accessory",
    summary="Добавить новый accessory",
    description="По факту добавить новый артикул и ассоциированные с ним данные",
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": {"description": "Successfully created new accessory"}
                }
            },
        },
        409: {
            "description": "Article already exists",
            "content": {
                "application/json": {
                    "example": {"description": "Article already exists"}
                }
            },
        },
    },
    tags=["storage"],
)
async def add_accessory(
    article: int = Form(...),
    name: str = Form(...),
    type: str = Form(...),
    width: int = Form(...),
    length: Optional[int] = Form(...),
    weight: Optional[int] = Form(...),
    price: float = Form(...),
    user: models.User = Depends(manager),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    same_article = (
        db.query(models.Accessory)
        .filter(models.Accessory.article == article)
        .one_or_none()
    )
    if same_article is not None:
        raise exceptions.ArticleAlreadyExists

    image_filename = await utils.save_file(image)

    new_accessory = models.Accessory(
        article=article,
        name=name,
        type=type,
        width=width,
        length=length,
        weight=weight,
        price=price,
        image=image_filename,
    )
    db.add(new_accessory)
    db.commit()
    db.flush()

    return JSONResponse(
        status_code=200, content={"description": "Successfully created new accessory"}
    )


@app.post(
    "/api/v1/cloth",
    summary="Добавить новую ткань",
    description="По факту добавить новый артикул и ассоциированные с ним данные",
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": {"description": "Successfully created new cloth"}
                }
            },
        },
        409: {
            "description": "Article already exists",
            "content": {
                "application/json": {
                    "example": {"description": "Article already exists"}
                }
            },
        },
    },
    tags=["storage"],
)
async def add_cloth(
    article: int = Form(...),
    color: str = Form(...),
    print: Optional[str] = Form(...),
    width: float = Form(...),
    name: str = Form(...),
    composition: str = Form(...),
    price: float = Form(...),
    image: UploadFile = File(...),
    user: models.User = Depends(manager),
    db: Session = Depends(get_db),
):
    same_article = (
        db.query(models.Cloth).filter(models.Cloth.article == article).one_or_none()
    )
    if same_article is not None:
        raise exceptions.ArticleAlreadyExists

    image_filename = await utils.save_file(image)

    new_cloth = models.Cloth(
        article=article,
        color=color,
        print=print,
        width=width,
        name=name,
        composition=composition,
        price=price,
        image=image_filename,
    )
    db.add(new_cloth)
    db.commit()
    db.flush()

    return JSONResponse(
        status_code=200, content={"description": "Successfully created new cloth"}
    )


@app.patch("/api/v1/cloth/{article}/{number}", tags=["storage"])
async def cloth_decommission(
    article: int,
    number: int,
    length: float,
    user: models.User = Depends(manager),
    db: Session = Depends(get_db),
):
    batch: Optional[models.ClothStorage] = (
        db.query(models.ClothStorage)
        .filter(
            models.ClothStorage.article == article, models.ClothStorage.number == number
        )
        .one_or_none()
    )
    if batch is None:
        raise exceptions.InvalidClothStorage

    if batch.length < length:
        raise exceptions.InsufficientClothLength

    batch.length -= length
    if math.fabs(batch.length) < 1e-10:
        db.delete(batch)
    db.commit()
    db.flush()

    return JSONResponse(
        status_code=200, content={"description": "Decommissioned successfully"}
    )


@app.patch("/api/v1/accessory/{article}", tags=["storage"])
async def accessory_decommission(
    article: int,
    quantity: int,
    user: models.User = Depends(manager),
    db: Session = Depends(get_db),
):
    batch: Optional[models.AccessoriesStorage] = (
        db.query(models.AccessoriesStorage)
        .filter(models.AccessoriesStorage.article == article)
        .one_or_none()
    )
    if batch is None:
        raise exceptions.InvalidClothStorage

    if batch.count < quantity:
        raise exceptions.InsufficientClothLength

    batch.count -= quantity
    if batch.count == 0:
        db.delete(batch)
    db.commit()
    db.flush()

    return JSONResponse(
        status_code=200, content={"description": "Decommissioned successfully"}
    )


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
    cloth_articles: str = Form(...),
    accessory_articles: str = Form(...),
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

    new_product: models.Product = models.Product()
    new_product.article = article
    new_product.name = name
    new_product.length = length
    new_product.width = width
    image_filename = await utils.save_file(image)
    new_product.image = image_filename
    new_product.comment = comment
    new_product.price = price
    db.add(new_product)
    db.flush()
    db.refresh(new_product)
    if update:
        prev: models.Product = (
            db.query(models.Product)
            .filter(models.Product.current_active == True, models.Product.article == article)
            .one_or_none()
        )
        if prev is None:
            raise exceptions.ArticleDoesNotExist
        prev.current_active = False
        print("prev.id = ", prev.id)
        prev.next_id = new_product.id
    db.flush()
    db.refresh(new_product)

    cloth_articles = json.loads(cloth_articles)
    accessory_articles = json.loads(accessory_articles)

    for cloth in cloth_articles:
        db.execute(
            models.ProductClothRelations.insert().values(
                product_id=new_product.id, cloth_article=cloth
            )
        )

    for accessory in accessory_articles:
        db.execute(
            models.ProductAccessoryRelations.insert().values(
                product_id=new_product.id, accessory_article=accessory
            )
        )

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
    "/api/v1/product/{article}/previous",
    response_model=List[schemas.Product],
    response_model_exclude={"previous"},
    tags=["products"],
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


@app.post("/api/v1/goods_arrival", tags=["storage"])
async def goods_arrival(
    accessories: Optional[str] = Form(None),
    clothes: Optional[str] = Form(None),
    user: models.User = Depends(manager),
    db: Session = Depends(get_db),
):
    doc: Document = Document()
    page: Page = Page()
    doc.append_page(page)
    counter = 1
    font_path: Path = Path(__file__).parent.parent / "tnr.ttf"
    print(font_path)
    font: Font = TrueTypeFont.true_type_font_from_file(font_path)

    layout: PageLayout = SingleColumnLayout(page)
    layout.add(
        Paragraph(
            "от «___» __________________ 2022г.",
            font=font,
            horizontal_alignment=Alignment.RIGHT,
        )
    )
    layout.add(
        Paragraph("НАКЛАДНАЯ  № _____", font=font, text_alignment=Alignment.CENTERED)
    )
    layout.add(Paragraph("От кого:_____________________________", font=font))
    layout.add(Paragraph("Кому:_______________________________", font=font))
    table = (
        FixedColumnWidthTable(
            number_of_columns=6,
            number_of_rows=20,
            column_widths=[
                Decimal(1),
                Decimal(4),
                Decimal(2),
                Decimal(2),
                Decimal(2),
                Decimal(2),
            ],
        )
        .add(Paragraph("№\nп / п", font=font))
        .add(Paragraph("Наименование", font=font))
        .add(Paragraph("Единица\nизмерения", font=font))
        .add(Paragraph("Количество", font=font))
        .add(Paragraph("Цена (руб.)", font=font))
        .add(Paragraph("Стоимость (руб.)", font=font))
    )

    if accessories is not None:
        accessories_json: Dict[int, int] = json.loads(accessories)

        for accessory, count in accessories_json.items():
            accessory_as_is: models.Accessory = (
                db.query(models.Accessory)
                .filter(models.Accessory.article == accessory)
                .one()
            )
            table.add(Paragraph(str(counter), font=font))
            counter += 1
            table.add(
                Paragraph(accessory_as_is.name + " " + str(accessory_as_is.article), font=font)
            )
            table.add(Paragraph("штуки", font=font))
            table.add(Paragraph(str(count), font=font))
            table.add(Paragraph(str(accessory_as_is.price), font=font))
            table.add(Paragraph(str(accessory_as_is.price * count), font=font))
            old_accessory: Optional[models.AccessoriesStorage] = (
                db.query(models.AccessoriesStorage)
                .filter(models.AccessoriesStorage.article == accessory)
                .one_or_none()
            )
            if old_accessory is None:
                db.add(models.AccessoriesStorage(article=accessory, count=count))
            else:
                old_accessory.count += count

    cloth_infos = []
    if clothes is not None:
        clothes_json = json.loads(clothes)
        for cloth, packs in clothes_json.items():
            for length in packs:
                cloth_as_is: models.Cloth = (
                    db.query(models.Cloth).filter(models.Cloth.article == cloth).one()
                )

                table.add(Paragraph(str(counter), font=font))
                counter += 1
                table.add(Paragraph(cloth_as_is.name + " " + str(cloth_as_is.article)), font=font)
                table.add(Paragraph("метры", font=font))
                table.add(Paragraph(str(length), font=font))
                table.add(Paragraph(str(cloth_as_is.price), font=font))
                table.add(Paragraph(str(float(cloth_as_is.price) * length), font=font))

                new_id_obj = (
                    db.query(func.max(models.ClothStorage.number).label("max_id"))
                    .scalar()
                )
                new_id = new_id_obj+1 if new_id_obj is not None else 1
                if new_id_obj is not None:
                    print(new_id_obj)
                    new_id = new_id_obj + 1
                cloth_m = models.ClothStorage(
                    article=cloth, length=length, number=new_id
                )
                db.add(cloth_m)
                db.flush()
                db.refresh(cloth_m)
                cloth_infos.append(
                    {
                        "number": cloth_m.number,
                        "article": cloth_m.article,
                        "length": length,
                    }
                )

    db.commit()

    layout.add(
        table.set_padding_on_all_cells(Decimal(3), Decimal(3), Decimal(3), Decimal(3))
    )
    layout.add(Paragraph("Сдал(Ф.И.О., подпись):_____________________", font=font))
    layout.add(Paragraph("Принял(Ф.И.О., подпись):______________________", font=font))

    filename = "static/" + secrets.token_hex(nbytes=16) + ".pdf"
    with open(filename, "wb") as out_file_handle:
        PDF.dumps(out_file_handle, doc)

    cloth_infos.append(filename)
    return cloth_infos
