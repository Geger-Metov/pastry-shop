"""Демо-данные для разработки: категории, товары, варианты, аллергены. Только данные, без логики."""

from dataclasses import dataclass
from decimal import Decimal

from app.domain.locale import Locale

type Texts = dict[Locale, tuple[str, str]]  # язык -> (название, описание)

ALLERGEN_CODES: tuple[str, ...] = ("gluten", "milk", "eggs", "nuts")


@dataclass(frozen=True, slots=True)
class CategorySeed:
    slug: str
    sort_order: int
    texts: Texts


@dataclass(frozen=True, slots=True)
class VariantSeed:
    price: Decimal
    weight_g: int | None = None
    pieces: int | None = None


@dataclass(frozen=True, slots=True)
class ProductSeed:
    slug: str
    category: str  # slug категории
    sort_order: int
    texts: Texts
    variants: tuple[VariantSeed, ...]
    images: tuple[str, ...]
    allergens: tuple[str, ...]


CATEGORIES: tuple[CategorySeed, ...] = (
    CategorySeed(
        slug="cakes",
        sort_order=1,
        texts={
            "ru": ("Торты", "Торты на заказ и из витрины"),
            "en": ("Cakes", "Cakes to order and from the display"),
            "fr": ("Gâteaux", "Gâteaux sur commande et en vitrine"),
        },
    ),
    CategorySeed(
        slug="macarons",
        sort_order=2,
        texts={
            "ru": ("Макаруны", "Миндальное печенье с кремом"),
            "en": ("Macarons", "Almond cookies with cream filling"),
            "fr": ("Macarons", "Biscuits aux amandes fourrés à la crème"),
        },
    ),
    CategorySeed(
        slug="pastries",
        sort_order=3,
        texts={
            "ru": ("Пирожные", "Эклеры, круассаны и другая выпечка"),
            "en": ("Pastries", "Éclairs, croissants and other pastries"),
            "fr": ("Pâtisseries", "Éclairs, croissants et autres viennoiseries"),
        },
    ),
)

PRODUCTS: tuple[ProductSeed, ...] = (
    ProductSeed(
        slug="napoleon",
        category="cakes",
        sort_order=1,
        texts={
            "ru": ("Наполеон", "Слоёный торт с заварным кремом"),
            "en": ("Napoleon", "Puff pastry cake with custard cream"),
            "fr": ("Napoléon", "Gâteau feuilleté à la crème pâtissière"),
        },
        variants=(
            VariantSeed(Decimal("1300.00"), weight_g=1000),
            VariantSeed(Decimal("2500.00"), weight_g=2000),
        ),
        images=("/images/products/napoleon-1.jpg", "/images/products/napoleon-2.jpg"),
        allergens=("gluten", "milk", "eggs"),
    ),
    ProductSeed(
        slug="medovik",
        category="cakes",
        sort_order=2,
        texts={
            "ru": ("Медовик", "Медовые коржи со сметанным кремом"),
            "en": ("Honey cake", "Honey layers with sour cream frosting"),
            "fr": ("Gâteau au miel", "Couches au miel et crème à la crème aigre"),
        },
        variants=(
            VariantSeed(Decimal("1200.00"), weight_g=1000),
            VariantSeed(Decimal("2300.00"), weight_g=2000),
        ),
        images=("/images/products/medovik-1.jpg",),
        allergens=("gluten", "milk", "eggs", "nuts"),
    ),
    ProductSeed(
        slug="cheesecake",
        category="cakes",
        sort_order=3,
        texts={
            "ru": ("Чизкейк", "Нежный сырный торт на песочной основе"),
            "en": ("Cheesecake", "Creamy cheese cake on a shortbread base"),
            "fr": ("Cheesecake", "Gâteau au fromage sur fond sablé"),
        },
        variants=(VariantSeed(Decimal("1500.00"), weight_g=1200),),
        images=("/images/products/cheesecake-1.jpg",),
        allergens=("gluten", "milk", "eggs"),
    ),
    ProductSeed(
        slug="macarons-assorted",
        category="macarons",
        sort_order=1,
        texts={
            "ru": ("Макаруны ассорти", "Набор макарун разных вкусов"),
            "en": ("Assorted macarons", "A box of macarons in different flavours"),
            "fr": ("Macarons assortis", "Boîte de macarons de saveurs variées"),
        },
        variants=(
            VariantSeed(Decimal("600.00"), pieces=6),
            VariantSeed(Decimal("1100.00"), pieces=12),
            VariantSeed(Decimal("2000.00"), pieces=24),
        ),
        images=("/images/products/macarons-1.jpg",),
        allergens=("nuts", "eggs"),
    ),
    ProductSeed(
        slug="eclair",
        category="pastries",
        sort_order=1,
        texts={
            "ru": ("Эклер", "Заварное пирожное с ванильным кремом"),
            "en": ("Éclair", "Choux pastry with vanilla cream"),
            "fr": ("Éclair", "Pâte à choux à la crème vanille"),
        },
        variants=(
            VariantSeed(Decimal("180.00"), pieces=1),
            VariantSeed(Decimal("950.00"), pieces=6),
        ),
        images=("/images/products/eclair-1.jpg",),
        allergens=("gluten", "milk", "eggs"),
    ),
    ProductSeed(
        slug="croissant",
        category="pastries",
        sort_order=2,
        texts={
            "ru": ("Круассан", "Масляный круассан"),
            "en": ("Croissant", "Classic butter croissant"),
            "fr": ("Croissant", "Croissant pur beurre"),
        },
        variants=(VariantSeed(Decimal("150.00"), pieces=1),),
        images=(),
        allergens=("gluten", "milk"),
    ),
)
