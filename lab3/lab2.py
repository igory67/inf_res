import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

class Connector:
    
    def __init__(self):
    
        self.conn = psycopg2.connect(dbname = 'lab2',
                            user = 'postgres',
                            password = '1234',
                            host = 'localhost',
                            client_encoding = "UTF8")
        
        self.cur = self.conn.cursor()
    

    def suic_table_name(self):
        return 'suic_table'
    

    def columns_without_id(self):
        return ['country',
                'year',
                'sex',
                'age',
                'suicides_no',
                'population',
                'suicides_100k_pop']
    

    def columns(self):
        return ['id',
                'country',
                'year',
                'sex',
                'age',
                'suicides_no',
                'population',
                'suicides_100k_pop']
    

    def sql_execute(self, sql, var = []):
        result = []
        try:
            self.cur.execute(sql, var)
            
            if 'select' in sql.lower():
                result = self.cur.fetchall()
            
            self.conn.commit()

        except Exception as e:
            print(f'Executing error - {e}')
            self.conn.rollback()
        
        return result
    

    def taska_creation(self):
        sex_fvar = 'female'
        sex_mvar = 'male'

        sql = 'create table if not exists suic_table(' \
                'id serial primary key,' \
                'country varchar(30), ' \
                'year integer, ' \
               f"sex varchar(6) check (sex = '{sex_fvar}' or sex = '{sex_mvar}'), " \
                'age varchar(12),' \
                'suicides_no integer, ' \
                'population integer, ' \
                'suicides_100k_pop numeric(5,2));'

        self.sql_execute(sql)
    

    def taskb_insert_into_table(self, var):
        
        for atr in var:
            atr = str(atr)
        
        sql = f'insert into {self.suic_table_name()} ({", ".join(self.columns_without_id())}) ' \
                f'values ( {", ".join(["%s"] * len(self.columns_without_id()))} )'
        
        self.sql_execute(sql, var)


def taskb_check_row(row):
    result = []

    if row['country'] is not None:
        result.append(str(row['country']))
    else:
        result.append(None)
    
    if row['year'] is not None:
        result.append(int(row['year']))
    else:
        result.append(None)
    
    if row['sex'] is not None:
        result.append(str(row['sex']))
    else:
        result.append(None)

    if row['age'] is not None:
        result.append(str(row['age']))
    else:
        result.append(None)
    
    if row['suicides_no'] is not None:
        result.append(int(row['suicides_no']))
    else:
        result.append(None)
    
    if row['population'] is not None:
        result.append(int(row['population']))
    else:
        result.append(None)
    
    if float(row['suicides/100k pop']) is not None:
        result.append(float(row['suicides/100k pop']))
    else:
        result.append(None)
    
    return result

def taskb_getting_info(filename):

    df = pd.read_csv(filename) # read csv 

    columns_needed = ['country', 'year', 'sex', 'age', 'suicides_no', 'population', 'suicides/100k pop'] #needed atr

    df_filtered = df[columns_needed] #filter columns
    df_filtered = df_filtered.replace({'': None})
    
    result_info = []
    
    for _, row in df_filtered.iterrows():
        values = taskb_check_row(row)
        result_info.append(values)
    
    return result_info
    
def taskb_uploading_info(db_conn : Connector, result_info):
    
    try:
        for row in result_info:
            db_conn.taskb_insert_into_table(row)

    except Exception as e:
        print(f' Error while uploading data - {e}')


def taskc_cleaning_resulting_info(filename):
    
    df = pd.read_csv(filename)

    original_count = len(df)
    
    # 1. deleting rows with at least one of this columns = NULL
    columns_needed = ['country', 'year', 'sex', 'age', 'suicides_no', 'population', 'suicides/100k pop']

    df = df.dropna(subset=columns_needed)
    
    # 2. sex filter
    df = df[df['sex'].isin(['male', 'female'])]
    
    # 3. year filter
    df = df[(df['year'] >= 1985) & (df['year'] <= 2016)]
    
    # 4. population filter
    df = df[df['population'] > 0]
    
    # 5. cnt suicide filter
    df = df[df['suicides_no'] >= 0]
    
    # 6. age filter
    valid_ages = ['5-14 years', '15-24 years', '25-34 years', 
                  '35-54 years', '55-74 years', '75+ years']
    
    df = df[df['age'].isin(valid_ages)]
    
    # 7. check formulas
    df['expected_rate'] = (df['suicides_no'] / df['population']) * 100000
    df['rate_diff'] = abs(df['suicides/100k pop'] - df['expected_rate'])
    df = df[df['rate_diff'] < 0.01]
    
    
    # deleting temp atr
    df = df.drop(['expected_rate', 'rate_diff'], axis=1)
    
    # deleting duplicates
    df = df.drop_duplicates()
    
    print(f"Data cleaning completed:")
    print(f"  - Original rows: {original_count}")
    print(f"  - Rows after cleaning: {len(df)}")
    print(f"  - Removed {original_count - len(df)} rows")
    
    return df


def taske_cleaning(df: pd.DataFrame) -> pd.DataFrame:
    countries_with_zero = df.loc[df['suicides_no'] == 0, 'country'].unique()
    result = df[~df['country'].isin(countries_with_zero)].reset_index(drop=True)
    return result

def taskd_sum_by_year(df : pd.DataFrame) -> list[int]:

    yearly_suicides = df.groupby('year')['suicides_no'].sum().reset_index()
    
    for _, row in yearly_suicides.iterrows():
        print('-'*40)
        print(f'year = {row["year"]} | party_no = {row["suicides_no"]}')
    return [row["suicides_no"] for _, row in yearly_suicides.iterrows()]


def taskf_plot_show(df : pd.DataFrame):

    #filter Russia
    russia_data = df[df['country'] == 'Russian Federation']
    
    if russia_data.empty:
        print("No data ebout Russian Federation")
        return
    
    # group and sum
    yearly_suicides = russia_data.groupby('year')['suicides_no'].sum().reset_index()
    
    #sorting values by year
    yearly_suicides = yearly_suicides.sort_values('year')
    
    # plotting
    plt.figure(figsize=(12, 6))
    plt.plot(yearly_suicides['year'], yearly_suicides['suicides_no'], linestyle='-', color='red')
    
    plt.title('parties per year in Russian Federation', fontsize=16, fontweight='bold')
    plt.xlabel('year', fontsize=12)
    plt.ylabel('party_no', fontsize=12)
    #plt.grid(True, alpha=0.3)
    plt.xticks(yearly_suicides['year'][::2], rotation=45)  # every second year
    
    # values for plot
    for _, row in yearly_suicides.iterrows():
        plt.annotate(f'{int(row["suicides_no"]):,}', 
                    (row['year'], row['suicides_no']),
                    textcoords="offset points", 
                    xytext=(0,8), 
                    ha='center', 
                    fontsize=7)
    
    plt.tight_layout()
    plt.show()

def taskg_compute_correlations(df: pd.DataFrame, col_x: str, col_y: str) -> dict:
    x = df[col_x].dropna()
    y = df[col_y].dropna()

    common_idx = x.index.intersection(y.index)
    x, y = x[common_idx], y[common_idx]

    pearson_r, pearson_p = stats.pearsonr(x, y)
    spearman_r, spearman_p = stats.spearmanr(x, y)

    results = {
        "pearson": {
            "r": round(pearson_r, 4),
            "p_value": round(pearson_p, 4),
        },
        "spearman": {
            "rho": round(spearman_r, 4),
            "p_value": round(spearman_p, 4),
        },
        "n": len(x),
    }
    return results


def main():
    #task a
    print('task a')
    db_conn = Connector()
    db_conn.taska_creation()
    print('creation completed\n')

    #task b
    print('task b')
    filename = 'master.csv'
    result_info = taskb_getting_info(filename)
    #taskb_uploading_info(db_conn, result_info)
    print('insertion completed\n')

    #task c
    print('task c')
    df = taskc_cleaning_resulting_info(filename)
    print(df.columns)
    print('cleaning completed\n')

    #task d
    print('task d')
    suicide_no_sum = taskd_sum_by_year(df)
    print('aggregation completed')

    #task e
    print('task e')
    df_clean = taske_cleaning(df)
    print(f"Before: {df['country'].nunique()} countries")
    print(f"After: {df_clean['country'].nunique()} countries")
    df = df_clean
    print('cleaning completed')

    #task f
    print('task f')
    taskf_plot_show(df)
    print('plot-showing completed')


    #task g
    data = {
        "years": list(range(1985, 2017)),
        "suicide_no": suicide_no_sum
    }
    corr_df = pd.DataFrame(data)

    print(str(taskg_compute_correlations(corr_df, "years", "suicide_no")).replace('\'', "\""))


if __name__ == "__main__":
    main()
