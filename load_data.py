import json
import pandas as pd

climate_jsonl = pd.read_json(path_or_buf='./data/climate-fever-dataset-r1.jsonl', lines=True)
health_jsonl = pd.read_json(path_or_buf='./data/pubhealthtab.jsonl', lines=True)


climate_dt = pd.DataFrame()
health_dt = pd.DataFrame()


climate_dt["sentence_id"] = climate_jsonl.claim_id
climate_dt["text"] = climate_jsonl.claim
climate_dt["label"] = climate_jsonl.claim_label
climate_dt.loc[climate_dt['label'] == 'SUPPORTS', 'label'] = 1
climate_dt.loc[climate_dt['label'] == 'REFUTES', 'label'] = 0
climate_dt.loc[climate_dt['label'] == 'DISPUTED', 'label'] = 0
climate_dt = climate_dt.drop(climate_dt[climate_dt.label == 'NOT_ENOUGH_INFO'].index)

health_dt["sentence_id"] = health_jsonl._id
health_dt["text"] = health_jsonl.claim
health_dt["label"] = health_jsonl.label
health_dt.loc[health_dt['label'] == 'SUPPORTS', 'label'] = 1
health_dt.loc[health_dt['label'] == 'REFUTES', 'label'] = 0
health_dt = health_dt.drop(health_dt[health_dt.label == 'NOT ENOUGH INFO'].index)

# convert dataframe to dictionary
json_list_climate = json.loads(json.dumps(list(climate_dt.T.to_dict().values())))
json_list_health = json.loads(json.dumps(list(health_dt.T.to_dict().values())))
joined_dataset = json_list_climate + json_list_health

# i = 0
# for block in joined_dataset:
#     block['sentence_id'] = i
#     i = i + 1

# save in json file
with open('climate_claims.json', 'w') as outfile:
    json.dump(json_list_climate, outfile)

with open('health_claims.json', 'w') as outfile:
    json.dump(json_list_health, outfile)

with open('data/two_class/climate_n_health_claims.json', 'w') as outfile:
    json.dump(joined_dataset, outfile)
