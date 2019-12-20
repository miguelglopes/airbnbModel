def removeOutliers(df, column, byCategory = None, onlyLower = False):
          
    if byCategory is None:
    
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1
        fence_low  = q1-1.5*iqr
        fence_high = q3+1.5*iqr
        filterRule= (df[column] < fence_low) | (df[column] > fence_high)
        if onlyLower:
            filterRule= (df[column] < fence_low)
        df_out = df.loc[~filterRule]
        return df_out
    
    else:
        
        df_out = df
        
        cats = df_out[byCategory].unique()
        for cat in cats:
            newDF = df_out[df_out[byCategory]==cat][column]
            q1 = newDF.quantile(0.25)
            q3 = newDF.quantile(0.75)
            iqr = q3 - q1
            fence_low  = q1-1.5*iqr
            fence_high = q3+1.5*iqr
            filterRule = (df_out[byCategory] == cat) & ((df_out[column] < fence_low) | (df_out[column] > fence_high))
            if onlyLower:
                filterRule= (df_out[byCategory] == cat) & (df_out[column] < fence_low)
            df_out = df_out.loc[~filterRule]

        return df_out
