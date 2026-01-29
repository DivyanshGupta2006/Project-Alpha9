import pandas as pd

def merge_split(data,
                symbols,
                train_start_date,
                val_start_date,
                test_start_date,
                train_dir,
                val_dir,
                test_dir,):
    # merge
    merged_data = pd.DataFrame()
    for symbol in symbols:
        df = data[symbol]
        for col in df.columns:
            df.rename(columns={col: (col, symbol)}, inplace=True)
        if merged_data.empty:
            merged_data = df
        else:
            merged_data = pd.merge(merged_data, df, how="inner", left_index=True, right_index=True)
    merged_data.dropna(inplace=True)

    # split
    data_train = merged_data[(train_start_date <= merged_data.index) & (merged_data.index < val_start_date)]
    data_val = merged_data[(val_start_date <= merged_data.index) & (merged_data.index < test_start_date)]
    data_test = merged_data[(test_start_date <= merged_data.index)]

    data_train.to_csv(train_dir / 'data.csv', index=True)
    data_val.to_csv(val_dir / 'data.csv', index=True)
    data_test.to_csv(test_dir / 'data.csv', index=True)

    return "Success"