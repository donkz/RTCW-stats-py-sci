df = pd.DataFrame()
df["a"] = [1,2,3,4,5,6,7]
df["b"] = [0,2,np.nan,4,5,6,7]
df["c"] = df["a"]/df["b"]
df["c"].astype(int) #error
df["c"].round(1)


nonadf = df.fillna(0)
nonadf["c"].astype(int) #still error on inf

pd.options.mode.use_inf_as_na = True
nonadf["c"].astype(int) #still error on inf because it's not autoreplaced

df = pd.DataFrame()
df["a"] = [1,2,3,4,5,6,7]
df["b"] = [0,2,np.nan,4,5,6,7]
df["c"] = df["a"]/df["b"]
df = df.fillna(0)
df["c"].astype(int)




