import pandas as pd
from sqlalchemy import create_engine


def remove_letter_mismatches_db():
    engine = create_engine('sqlite:///phosphosite_orthology_merged.db')  # create db in outside directory

    # database where row must have matching phosphosite type (e.g. not S in one organism and T in the other on the same row)
    engine_out = create_engine('sqlite:///phosphosite_orthology_cleaned.db')  # create db in outside directory


    table_iter = engine.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_list = [i[0] for i in table_iter]

    #print(table_list)

    for i in table_list:
        df = pd.read_sql_table(i, con=engine)
        column_list = list(df.columns)
        #print(column_list)
        phos_type_headers = [i for i in column_list if i.startswith('Type_')]
        #print(phos_type_headers)

        # dataframe only keeps rows where Type_HUMAN == Type_OTHER
        df = df[df[phos_type_headers[0]] == df[phos_type_headers[1]]]
        #print(df.head())
        df.to_sql(i, engine_out, index=False, if_exists='replace', chunksize=10000)

if __name__ == '__main__':
    remove_letter_mismatches_db()