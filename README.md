# Project Name: EATinerary
## Members: Brian Haley and Anna Francesca Gatus
### [EATinerary project](https://github.com/users/TotalEntropy/projects/2)
### Linked repos: [EATinerary-ETL](https://github.com/TotalEntropy/Eatinerary.git)
#### Purpose
The purpose of this repo is to take the [Yelp Dataset](https://www.yelp.com/dataset/download) and perform the ETL process for the [EATinerary app](https://github.com/TotalEntropy/EATinerary.git).

#### Requirements
1. Python=3.6.8
2. pip
3. PyMySQL==0.9.3
4. pandas==0.24.2
5. numpy==1.16.4
6. SQLAlchemy==1.3.5

#### Steps
1. Download the [Yelp Dataset JSON](https://www.yelp.com/dataset/download) and place it in the [Source data forder](https://github.com/TotalEntropy/Eatinerary-ETL/tree/master/sourceData)
2. Create a config.py in the [Eatinerary-ETL folder](https://github.com/TotalEntropy/Eatinerary-ETL) and include ```conn=user:pass@host```
3. Run either [ETL.py](https://github.com/TotalEntropy/Eatinerary-ETL/blob/master/ETL.py) or [ETL.ipynb](https://github.com/TotalEntropy/Eatinerary-ETL/blob/master/ETL.ipynb)
4. Head over to [EATinerary app](https://github.com/TotalEntropy/EATinerary.git)!
