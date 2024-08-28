import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

df = pd.read_csv('Main.csv')
def_df = pd.read_csv('passing_yards.csv')

df = df[['Rk', 'Player', 'Yds', 'Date', 'Opp', 'Cmp', 'Att']]
df.Date = df.Date.astype('datetime64[D]')
df['Date_add'] = -3
df.Date_add = df.Date_add.astype('timedelta64[M]')
df['Season'] = df.Date + df.Date_add
df.Season = df.Season.dt.year
df = df[['Rk', 'Player', 'Yds', 'Season', 'Opp', 'Cmp', 'Att']]

def_df_grouped = def_df.groupby(['Team', 'Season']).sum()
def_df_grouped = def_df_grouped[['Yds']]
def_df_grouped = def_df_grouped.reset_index()

q0 = def_df_grouped.Yds.min()
q1 = def_df_grouped.Yds.quantile(.25)
q2 = def_df_grouped.Yds.quantile(.5)
q3 = def_df_grouped.Yds.quantile(.75)
q4 = def_df_grouped.Yds.max()

def categorize(x):
    if x >= q3:
        return 4
    elif x >= q2:
        return 3
    elif x >= q1:
        return 2
    else:
        return 1

def_df_grouped['Quartile'] = def_df_grouped.Yds.apply(categorize)

df_joined = df.merge(def_df_grouped, how='left', left_on=['Opp', 'Season'], right_on=['Team', 'Season'])

df_qbs = df[['Rk', 'Player']]
df_qb_counts = df_qbs.groupby('Player').count()

df_joined = df_joined.merge(df_qb_counts, how='left', on='Player')
df_joined = df_joined[df_joined.Rk_y >= 10]

df_joined_2 = df_joined[['Rk_x', 'Player']]
df_joined_2_grouped = df_joined_2.groupby('Player').mean().sort_values('Rk_x')

df_joined_wanted = df_joined[['Player', 'Yds_x', 'Quartile']]
df_joined_wanted2 = df_joined[['Yds_x', 'Quartile']]
df_qb_by_quartile = df_joined_wanted.groupby(['Player', 'Quartile']).mean()
df_qb_by_quartile = df_qb_by_quartile.reset_index()

df_avg_qb = df_qb_by_quartile[['Quartile', 'Yds_x']]
df_avg_qb = df_avg_qb.groupby('Quartile').mean()

df_avg_qb_pivot = df_qb_by_quartile.pivot(columns='Quartile', index='Player', values='Yds_x').reset_index()

df_avg_qb2 = df_joined_wanted2.groupby('Quartile').mean()

#print(q0, q1, q2, q3, q4)
#print(df_avg_qb_pivot)
#print(df_avg_qb2)

def change_detector(x, y):
    if x <= y:
        return 1
    else:
        return -1

df_avg_qb_pivot.columns = ['Player', 'one', 'two', 'three', 'four']
df_avg_qb_pivot['one_two'] = df_avg_qb_pivot.apply(lambda x: change_detector(x['one'], x['two']), axis=1)
df_avg_qb_pivot['two_three'] = df_avg_qb_pivot.apply(lambda x: change_detector(x['two'], x['three']), axis=1)
df_avg_qb_pivot['three_four'] = df_avg_qb_pivot.apply(lambda x: change_detector(x['three'], x['four']), axis=1)

def shape(x, y, z):
    if x == 1:
        if y == 1:
            if z == 1:
                return "Expected"
            else:
                return "QB Pulled?"
        else:
            if z == 1:
                return "Trap Games?"
            else:
                return "Pulled Early?"
    else:
        if y == 1:
            if z == 1:
                return "Clutch"
            else:
                return "Clutch Protected"
        else:
            if z == 1:
                return "Gamer?"
            else:
                return "WTF?"

df_avg_qb_pivot['type'] = df_avg_qb_pivot.apply(lambda x: shape(x['one_two'], x['two_three'], x['three_four']), axis=1)

print(df_avg_qb_pivot)

df_avg_qb_pivot.to_csv('qb_quartile_analysis.csv', index = False)

"""
for name in df_qb_by_quartile.Player.unique():
    df_qb = df_qb_by_quartile[df_qb_by_quartile.Player == name]
    plt.plot(df_qb.Quartile, df_qb.Yds_x)
    plt.title(name)
    plt.show()
"""
#print(df.dtypes)