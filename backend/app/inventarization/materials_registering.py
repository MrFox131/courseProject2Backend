import json
import secrets
from decimal import Decimal
from pathlib import Path
from typing import List, Optional, Dict, Union

from borb.pdf.canvas.font.font import Font
from borb.pdf.canvas.font.simple_font.true_type_font import TrueTypeFont
from borb.pdf.canvas.layout.layout_element import Alignment
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.page_layout.page_layout import PageLayout
from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.document import Document
from borb.pdf.page.page import Page
from borb.pdf.pdf import PDF
from fastapi import Depends, Form, UploadFile, File  #
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import exceptions
from .. import schemas
from .. import utils
from ..db import get_db, models
from ..main import app, manager


@app.get("/api/v1/cloth", response_model=List[schemas.Cloth], tags=["storage"])
async def get_clothes(
    user: models.User = Depends(manager), db: Session = Depends(get_db)
):
    if user.role not in [
        models.UserType.chef,
        models.UserType.manager,
        models.UserType.storage_manager,
    ]:
        raise exceptions.InsufficientPrivileges
    return db.query(models.Cloth).all()


@app.get("/api/v1/accessory", response_model=List[schemas.Accessory], tags=["storage"])
async def get_accessories(
    user: models.User = Depends(manager), db: Session = Depends(get_db)
):
    if user.role not in [
        models.UserType.chef,
        models.UserType.manager,
        models.UserType.storage_manager,
    ]:
        raise exceptions.InsufficientPrivileges
    return db.query(models.Accessory).all()


@app.get(
    "/api/v1/accessory_by_id/{article}",
    response_model=schemas.Accessory,
    tags=["storage"],
)
async def get_accessories(
    article: int, user: models.User = Depends(manager), db: Session = Depends(get_db)
):
    if user.role not in [
        models.UserType.chef,
        models.UserType.manager,
        models.UserType.storage_manager,
    ]:
        raise exceptions.InsufficientPrivileges
    return db.query(models.Accessory).filter(models.Accessory.article == article).one()


@app.get("/api/v1/cloth_by_id/{article}")
async def cloth_by_article(
    article: int, user: models.User = Depends(manager), db: Session = Depends(get_db)
):
    if user.role not in [
        models.UserType.chef,
        models.UserType.manager,
        models.UserType.storage_manager,
    ]:
        raise exceptions.InsufficientPrivileges
    return db.query(models.Cloth).filter(models.Cloth.article == article).one()


@app.get(
    "/api/v1/cloth/{article}",
    response_model=List[schemas.ClothStorage],
    tags=["storage"],
)
async def get_cloth_packs(
    article: int, user: models.User = Depends(manager), db: Session = Depends(get_db)
):
    if user.role not in [
        models.UserType.chef,
        models.UserType.manager,
        models.UserType.storage_manager,
    ]:
        raise exceptions.InsufficientPrivileges
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
    if user.role not in [
        models.UserType.chef,
        models.UserType.manager,
        models.UserType.storage_manager,
    ]:
        raise exceptions.InsufficientPrivileges
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
    if user.role not in [
        models.UserType.chef,
        models.UserType.manager,
        models.UserType.storage_manager,
    ]:
        raise exceptions.InsufficientPrivileges
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
    weight: Optional[float] = Form(...),
    kg_acceptable: bool = Form(False),
    price: float = Form(...),
    user: models.User = Depends(manager),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if user.role not in [
        models.UserType.chef,
        models.UserType.manager,
        models.UserType.former_employee,
    ]:
        raise exceptions.InsufficientPrivileges
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
        kg_acceptable=kg_acceptable,
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
    font_path: Path = Path(__file__).parent / "tnr.ttf"
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
        accessories_json: Dict[int, Union[int, float]] = json.loads(accessories)

        for accessory, count in accessories_json.items():
            accessory_as_is: models.Accessory = (
                db.query(models.Accessory)
                .filter(models.Accessory.article == accessory)
                .one()
            )
            if not accessory_as_is.kg_acceptable and count is float:
                raise RequestValidationError
            table.add(Paragraph(str(counter), font=font))
            counter += 1
            table.add(
                Paragraph(
                    accessory_as_is.name + " " + str(accessory_as_is.article), font=font
                )
            )
            table.add(
                Paragraph(
                    "штуки" if not accessory_as_is.kg_acceptable else "кг", font=font
                )
            )
            table.add(Paragraph(str(count), font=font))
            table.add(Paragraph(str(accessory_as_is.price), font=font))
            table.add(
                Paragraph(
                    str(
                        (
                            (float(accessory_as_is.price) * count)
                            if not accessory_as_is.kg_acceptable
                            else (
                                float(accessory_as_is.price)
                                * round((count / accessory_as_is.weight))
                            )
                        )
                    ),
                    font=font,
                )
            )
            old_accessory: Optional[models.AccessoriesStorage] = (
                db.query(models.AccessoriesStorage)
                .filter(models.AccessoriesStorage.article == accessory)
                .one_or_none()
            )
            if old_accessory is None:
                db.add(models.AccessoriesStorage(article=accessory, amount=count))
            else:
                if not accessory_as_is.kg_acceptable:
                    old_accessory.amount += Decimal(count)
                else:
                    old_accessory.amount += Decimal(round((count / accessory_as_is.weight)))

            new_income = models.AccessoryChanges()
            if accessory_as_is.kg_acceptable:
                new_income.amount = count // accessory_as_is.weight
            else:
                new_income.amount = count
            new_income.is_income = True
            new_income.accessory_article = accessory
            db.add(new_income)

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
                table.add(
                    Paragraph(
                        cloth_as_is.name + " " + str(cloth_as_is.article), font=font
                    )
                )
                table.add(Paragraph("метры", font=font))
                table.add(Paragraph(str(length), font=font))
                table.add(Paragraph(str(cloth_as_is.price), font=font))
                table.add(Paragraph(str(float(cloth_as_is.price) * length), font=font))

                new_id_obj = db.query(
                    func.max(models.ClothStorage.number).label("max_id")
                ).scalar()
                new_id = new_id_obj + 1 if new_id_obj is not None else 1
                if new_id_obj is not None:
                    print(new_id_obj)
                    new_id = new_id_obj + 1
                cloth_m = models.ClothStorage(
                    article=cloth, length=length, number=new_id
                )

                new_income = models.ClothChanges()
                new_income.length = length
                new_income.is_income = True
                new_income.number = new_id
                new_income.cloth_article = cloth
                db.add(new_income)

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
