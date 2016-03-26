# Architek
Architek is a predictive analytics prototype for buildings.  Using machine learning, historical user and weather data, the prediction model provides advance information to the building management system (BMS), allowing the building to better manage resources and anticipate occupant load demands, which reduces energy consumption, reduce operating costs and provides healthier indoor environments.

## Motivation
Buildings consume nearly half of all the energy produced and responsible for nearly half of carbon emissions in the United States, significantly more than all the vehicles on the road.  The mechanical and electrical systems of a building approaches 70% of a buildings energy usage.  Currently, these systems are reactive, instead of predictive.

<img src=images/co2-energy.png width=400 height=200 />

## Goals / Solution
Reduce building energy consumption, reduce operating costs and provide healthier indoor environments with increased use of natural ventilation. Understand time series correlations between weather and building occupancy data to predict future short term demand.  I believe that significant cost and energy can be saved if the building automation system is able to anticipate demand.

## Approach
There are two main factors that determine heating and cooling loads: the temperature outside and the number of occupants inside.

A few hours before we all arrive for work in the morning, a building typically starts up and pre-heats or pre-cools our workspace.  It does this without knowing how many people are coming to work and what temperature it will be outside.

What if buildings knew this information ahead of time?  Based on consultations with energy experts, we can save energy if the building was more proactive with advanced predicted data.

<img src=images/weather-occupancy.png width=400 height=200 />

For this high-level approach, BART data will be used to infer the percentage of people going to work in downtown San Francisco.   Weather data will also be used to see if it affects work attendance.

<img src=images/bart-weather.png width=400 height=200 />

## Time Series Analysis

Based on morning commute data to downtown San Francisco, below is a graph showing how many people go to work by season.  Less people work during winter months, and on a weekly basis, Mondays and Fridays tend to be slower.

<img src=images/work-by-season.png width=600 height=300 />

The chart below shows that we have nice weather for about half the year.  We should be able to use more natural air during work hours and this would result in a healthier environment while saving energy.

<img src=images/outside-temp.png width=600 height=300 />

The chart below shows a cross correlation analysis between temperature and bart series data.  The top chart shows that warm weather correlates to an increase in bart ridership.  The bottom chart shows that an increase in pressure indicates a drop in bart ridership in the coming weeks.  Turns out that atmospheric pressure is a good indicator of future weather.

<img src=images/cross-correlation.png width=600 height=300 />

## Machine Learning

These features were used in a random forest machine learning model.  Overall, weather was not a huge factor in predicting work attendance in San Francisco because of the mild weather.  But using the same model on chicago and the weather was more of a factor because of the extreme temperatures there.  However, the accuracies are quite high, suggesting that our seasonal schedules are quite predictable.

<img src=images/random-forest-features.png width=600 height=300 />

## Data Pipeline

Used 5 years of weather and bart data in time series analysis which helped create features for the random forest model.  Hourly weather forecasts are pulled via API, processed and stored in a Postgres SQL database and then forecast how many people are going to work every day.


## Cost, Energy and Emissions Reduction Calculations

In conclusion and to get some insight, I did some back of the envelope calculations to see the impact if we used predictive analytics in our buildings.  I consulted energy experts and decided on a 5% energy reduction as a conservative estimate based on existing use cases.

<img src=images/calcs.png width=400 height=175 />

In total there are more than 1700 commercial buildings in san francisco.  so what if all these buildings used a predictive system?

Turns out the results are quite staggering with more than 1 billion dollars saved.

<img src=images/results.png width=400 height=150 />

<img src=images/logo.png width=200 height=75 />
