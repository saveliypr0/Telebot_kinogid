from sqlalchemy import Table, Column, Integer, String, MetaData

metadata_obj = MetaData()


favoriteF_table = Table(
    "favorite_films",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name_film", String)
)