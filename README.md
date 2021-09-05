# pulse-plus
Utilities to explore, convert PhonePe [Pulse data](https://github.com/PhonePe/pulse)

# Installation

1. Checkout the repo.
2. Install dependencies. `poetry install`. Use Python 3.9
3. Now the installation should have all the dependencies.
4. Check out the pulse data repo - https://github.com/PhonePe/pulse

# Usage

1. Convert the data directory into sqlite db.

   ```bash
   $poetry run python pulse/cli.py ../pulse/data --output pulse.db
   aggregated_user table created
   aggregated_user_device table created
   aggregated_transaction table created
   top_user table created
   top_transaction table created
   Inserted 5698 records in aggregated_user_device
   Inserted 518 records in aggregated_user
   Inserted 2584 records in aggregated_transaction
   Inserted 9562 records in top_user
   Inserted 9561 records in top_transaction
   pulse.db created
   ```

2. Check the created database

   ```bash
   $poetry run sqlite-utils pulse.db 'select count(*) from aggregated_user' -t
     count(*)
   ----------
          518
   $poetry run sqlite-utils pulse.db 'select * from aggregated_user limit 1' -t
     id  aggregated_by    aggregate_name               year    users    app_opens  start_date    end_date
   ----  ---------------  -------------------------  ------  -------  -----------  ------------  ----------
      1  state            andaman-&-nicobar-islands    2019    18596            0  2019-01-01    2019-03-31
   
   ```

   

   

   ## All tables schema

   

   ```sql
   CREATE TABLE [aggregated_user] (
      [id] INTEGER PRIMARY KEY NOT NULL,
      [aggregated_by] TEXT NOT NULL,
      [aggregate_name] TEXT NOT NULL,
      [year] INTEGER NOT NULL,
      [users] INTEGER NOT NULL,
      [app_opens] INTEGER NOT NULL,
      [start_date] TEXT NOT NULL,
      [end_date] TEXT NOT NULL
   );
   CREATE TABLE [aggregated_user_device] (
      [id] INTEGER PRIMARY KEY NOT NULL,
      [aggregated_by] TEXT NOT NULL,
      [aggregate_name] TEXT NOT NULL,
      [year] INTEGER NOT NULL,
      [start_date] TEXT NOT NULL,
      [end_date] TEXT NOT NULL,
      [brand] TEXT NOT NULL,
      [count] INTEGER NOT NULL,
      [percentage] FLOAT NOT NULL
   );
   CREATE TABLE [aggregated_transaction] (
      [id] INTEGER PRIMARY KEY NOT NULL,
      [aggregated_by] TEXT NOT NULL,
      [aggregate_name] TEXT NOT NULL,
      [year] INTEGER NOT NULL,
      [start_date] TEXT NOT NULL,
      [end_date] TEXT NOT NULL,
      [name] TEXT NOT NULL,
      [type] TEXT NOT NULL,
      [count] INTEGER NOT NULL,
      [amount] FLOAT NOT NULL
   );
   CREATE TABLE [top_user] (
      [id] INTEGER PRIMARY KEY NOT NULL,
      [aggregated_by] TEXT NOT NULL,
      [aggregate_name] TEXT NOT NULL,
      [year] INTEGER NOT NULL,
      [start_date] TEXT NOT NULL,
      [end_date] TEXT NOT NULL,
      [name] TEXT NOT NULL,
      [type] TEXT NOT NULL,
      [registered_users] INTEGER NOT NULL
   );
   CREATE TABLE [top_transaction] (
      [id] INTEGER PRIMARY KEY,
      [aggregated_by] TEXT,
      [aggregate_name] TEXT,
      [year] INTEGER,
      [start_date] TEXT,
      [end_date] TEXT,
      [entity_name] TEXT,
      [entity_type] TEXT,
      [type] TEXT,
      [count] INTEGER,
      [amount] FLOAT
   );
   
   ```

# Functionalities

- Convert the pulse repo into single sqlite db.
- Converted sqlite [database](data/v1/pulse.db) and five csv files: [data/v1/aggregated_user_device.csv](data/v1/aggregated_user_device.csv), [data/v1/aggregated_user.csv](data/v1/aggregated_user.csv), [data/v1/aggregated_transaction.csv](data/v1/aggregated_transaction.csv), [data/v1/top_transaction.csv](data/v1/top_transaction.csv), [data/v1/top_user.csv](data/v1/top_user.csv).

# CSV sample 

```bash
$head -4 data/v1/top_user.csv
id,aggregated_by,aggregate_name,year,start_date,end_date,name,type,registered_users
1,state,andaman-&-nicobar-islands,2019,2019-01-01,2019-03-31,744103,pincodes,4136
2,state,andaman-&-nicobar-islands,2019,2019-01-01,2019-03-31,744101,pincodes,3030
3,state,andaman-&-nicobar-islands,2019,2019-01-01,2019-03-31,744105,pincodes,2994

$head -4 data/v1/top_transaction.csv
id,aggregated_by,aggregate_name,year,start_date,end_date,entity_name,entity_type,type,count,amount
1,state,andaman-&-nicobar-islands,2019,2019-01-01,2019-03-31,744103,pincodes,TOTAL,5742,19401964.77965755
2,state,andaman-&-nicobar-islands,2019,2019-01-01,2019-03-31,744101,pincodes,TOTAL,5156,15501306.227195919
3,state,andaman-&-nicobar-islands,2019,2019-01-01,2019-03-31,744102,pincodes,TOTAL,3925,16683547.094795756

$head -4 data/v1/aggregated_transaction.csv
id,aggregated_by,aggregate_name,year,start_date,end_date,name,type,count,amount
1,state,andaman-&-nicobar-islands,2019,2019-01-01,2019-03-31,Recharge & bill payments,TOTAL,15263,6611459.8729725825
2,state,andaman-&-nicobar-islands,2019,2019-01-01,2019-03-31,Peer-to-peer payments,TOTAL,13119,91808345.86839552
3,state,andaman-&-nicobar-islands,2019,2019-01-01,2019-03-31,Merchant payments,TOTAL,1759,3266589.8469614363
```



