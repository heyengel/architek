# Architek AI: predictive analytics for buildings
Architek is a predictive analytics prototype for buildings.  Using machine learning, historical user and weather data, the prediction model provides advance information to the building management system (BMS), allowing the building to better manage resources and anticipate occupant load demands, which reduces energy consumption, reduce operating costs and provides healthier indoor environments.

**Project website: http://www.architek.live**

## Motivation
Buildings consume nearly half of all the energy produced and responsible for nearly half of carbon emissions in the United States, significantly more than all the vehicles on the road.  The mechanical and electrical systems of a building approaches 70% of a buildings energy usage.  Currently, these systems are reactive, instead of predictive.

<img src=images/co2-energy.png width=600 />

## Goals / Solution
Reduce building energy consumption, reduce operating costs and provide healthier indoor environments with increased use of natural ventilation. Understand time series correlations between weather and building occupancy data to predict future short term demand.  I believe that significant cost and energy can be saved if the building automation system is able to anticipate demand.

## Approach
There are two main factors that determine heating and cooling loads: the temperature outside and the number of occupants inside. A few hours before we all arrive for work in the morning, a building typically starts up and pre-heats or pre-cools our workspace.  It does this without knowing how many people are coming to work and what temperature it will be outside.

What if buildings knew this information ahead of time?  Based on consultations with energy experts, we can save energy if the building was more proactive with advanced predicted data.

<img src=images/weather-occupancy.png width=600 />

For this high-level approach, BART data was used to infer the percentage of people going to work in downtown San Francisco.  Weather data will also be used to determine if it affects work attendance.

<img src=images/bart-weather.png width=600 />

## Time Series Analysis

Based on morning commute data to downtown San Francisco, below is a graph showing how many people go to work by season.  Less people work during winter months, and on a weekly basis, Mondays and Fridays tend to be slower.

<img src=images/work-by-season.png width=600 />

The chart below shows that we have nice weather for about half the year.  We should be able to use more natural air during work hours and this would result in a healthier environment while saving energy.

<img src=images/outside-temp.png width=600 />

The chart below shows a cross correlation analysis between temperature and bart series data.  The top chart shows that warm weather correlates to an increase in bart ridership.  The bottom chart shows that an increase in pressure indicates a drop in bart ridership in the coming weeks.  Turns out that atmospheric pressure is a good indicator of future weather.

<img src=images/cross-correlation.png width=600 />

## Machine Learning

These features were used in a random forest machine learning model.  Overall, weather was not a big factor in predicting work attendance in San Francisco because of the mild weather.  The model was tested on Chicago For comparison, and the weather was more of a factor because of its extreme temperatures.  However, the prediction accuracies for both cities are still quite high, suggesting that our seasonal schedules are quite predictable.

<img src=images/random-forest-features.png width=600 />

## Data Pipeline

Used 5 years of weather and BART data in time series analysis which helped create features for the random forest model.  Weather forecasts are requested via API daily, and then processed and stored in a Postgres SQL database.  The prediction model then forecasts an estimate of the number of office workers in downtown San Francisco every day.

<img src=images/data-pipeline.png width=600 />


## Cost, Energy and Emissions Reduction Calculations

In conclusion and to get some insight, back of the envelope calculations were performed to determine the potential impact if we used predictive analytics in our buildings.  I consulted energy experts and established a 5% energy reduction as a conservative estimate based on existing use cases.

<img src=images/calcs.png width=600 />

In total there are more than 1700 commercial buildings in San Francisco.  What if all these buildings used a predictive system?  It turns out that the results are quite staggering with potentially more than 1 billion dollars saved, as well as significant savings in CO2 emissions and energy.

<img src=images/results.png width=600 />

## Future work

This project demonstrates the potential benefits of predictive analytics in our buildings. The prediction model is a highly scaleable solution and we can only begin to imagine the potential benefits globally.  Future work towards implementation has been identified, which includes acquiring more building specific data and validating cost and savings calculations.  Seasonal and individual work patterns appear to be significant factors in predicting our work schedules and should be incorporated into the model.  Hourly occupancy data can be incorporated to allow more fine-grained predictions which could lead to more cost and energy savings.

<img src=images/future-work.png width=600 />

## Toolbox
<dl class="dl-horizontal">
  <dt>Python</dt> <dd>scripting language that you can <a href="https://www.explainxkcd.com/wiki/images/f/fd/python.png">fly with</a></dd>
  <dt>Pandas</dt> <dd>exploratory data analysis, data wrangling</dd>
  <dt>Sci-kit Learn</dt> <dd>machine learning</dd>
  <dt>Numpy/Matplotlib</dt> <dd>cross correlation time series analysis</dd>
  <dt>Postgres</dt> <dd>SQL database</dd>
  <dt>Psycopg2</dt> <dd>SQL database adapter for python</dd>
  <dt>Flask-Bootstrap</dt> <dd>web app framework</dd>
  <dt>AWS</dt> <dd>host web app, cloud data storage</dd>

<img src=images/logo.png width=250 />
