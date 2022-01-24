import re
import pandas as pd

class SimilarityJoin:
    def __init__(self, data_file1, data_file2):
        self.df1 = pd.read_csv(data_file1)
        self.df2 = pd.read_csv(data_file2)
          
    def preprocess_df(self, df, cols): 
        """
            Write your code!
        """ 
        df['joinKey'] = ""
        df['joinKey'] = df[cols].apply(lambda x: x.str.cat(sep=' '), axis=1)
        df["joinKey"] = df["joinKey"].str.lower()
        df["joinKey"] = df["joinKey"].str.split(r'\W+')
        return df
    
    def filtering(self, df1, df2):
        """
            Write your code!
        """
        df1['joinKey1'] = df1['joinKey']
        df2['joinKey2'] = df2['joinKey']
        df1_explode = df1.explode('joinKey')
        df2_explote = df2.explode('joinKey')
        df_result = df1_explode.merge(df2_explote, on='joinKey')[['id_x','id_y','joinKey1', 'joinKey2']].rename(columns={"id_x":"id1", "id_y":"id2"})
        df_result = df_result.drop_duplicates(['id1','id2'])
        df_result.drop(df_result.columns[df_result.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)
        return df_result
      
    def verification(self, cand_df, threshold):
        """
            Write your code!
        """
        cand_df['jaccard_abslength']  = cand_df.apply(lambda x: len(x.joinKey1) + len(x.joinKey2), axis=1)
        cand_df['inter'] = cand_df.apply(lambda x : len([value for value in x.joinKey1 if value in x.joinKey2]), axis=1)
        cand_df['inter'] = cand_df.apply(lambda x : x.inter if x.inter < min(len(x.joinKey1), len(x.joinKey2)) else min( len(x.joinKey1), len(x.joinKey2)), axis=1)
        cand_df['jaccard'] = cand_df['inter']/ (cand_df['jaccard_abslength'] - cand_df['inter'])
        cand_df = cand_df[cand_df['jaccard']>=threshold]
        cand_df = cand_df[['id1','id2', 'joinKey1', 'joinKey2', 'jaccard']]
        return cand_df
        
    def evaluate(self, result, ground_truth):
        """
            Write your code!
        """
        precision = len([value for value in result if value in ground_truth])/len(result)
        recall =  len([value for value in result if value in ground_truth])/len(ground_truth)
        FMeasure = 2*precision*recall / (precision+recall)
        return precision, recall, FMeasure
        
    def jaccard_join(self, cols1, cols2, threshold):
        new_df1 = self.preprocess_df(self.df1, cols1)
        new_df2 = self.preprocess_df(self.df2, cols2)
        print ("Before filtering: %d pairs in total" %(self.df1.shape[0] *self.df2.shape[0])) 
        
        cand_df = self.filtering(new_df1, new_df2)
        print ("After Filtering: %d pairs left" %(cand_df.shape[0]))
        
        result_df = self.verification(cand_df, threshold)
        print ("After Verification: %d similar pairs" %(result_df.shape[0]))
        
        return result_df
       
        

if __name__ == "__main__":
    er = SimilarityJoin("Amazon_sample.csv", "Google_sample.csv")
    # er = SimilarityJoin("A2-data/part1-similarity-join/Amazon-Google-Sample/Amazon_sample.csv","A2-data/part1-similarity-join/Amazon-Google-Sample/Google_sample.csv")
    amazon_cols = ["title", "manufacturer"]
    google_cols = ["name", "manufacturer"]
    result_df = er.jaccard_join(amazon_cols, google_cols, 0.5)

    result = result_df[['id1', 'id2']].values.tolist()
    ground_truth = pd.read_csv("Amazon_Google_perfectMapping_sample.csv").values.tolist()
    print ("(precision, recall, fmeasure) = ", er.evaluate(result, ground_truth))