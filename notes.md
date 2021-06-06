# Notes

## Warm-up ticket #1

**Solution:**

I just added the following line at the end of the `openPopup` function.

```javascript
popup.setContent(content);
```

**How I resolved it:**

* When opening the page, I saw that the popup would open, but be empty.
* I saw in the code that a message was being added to the variable `content`, but that that variable was never used.
* I looked up the documentation for leaflet, specifically the part about the `L.popup` object. I saw that it has a method `setContent(<String|HTMLElement|Function> htmlContent` ([see Leaflet documentation](https://leafletjs.com/reference-1.7.1.html#popup-setcontent)). I added that method and it worked.

## Warm-up ticket #2

**Solution:**

* The query returns a table of countries. For each country, it provides the number of populated places it has, and the total population of the country.
* If a country exists in the database, but none of the populated places are inside it, the country would not appear in the result.
* A place is counted towards a country's number of places and total population if the geometric definition of the country and the place share any point. That means that in theory, it could be possible that a place (and its population) are counted for more than one country, given that their geometric definitions overlap.

**Example:**

The tables in the database could look something like this:

* european_countries:

| id   | name   | the_geom  |
| ---- | ------ | --------- |
| 1    | Spain  | <GeoJSON> |
| 2    | Italy  | <GeoJSON> |
| 3    | France | <GeoJSON> |

* populated_places:

| id   | name    | population | the_geom  |
| ---- | ------- | ---------- | --------- |
| 101  | Sevilla | 600        | <GeoJSON> |
| 102  | Madrid  | 1500       | <GeoJSON> |
| 103  | Paris   | 3000       | <GeoJSON> |

*The fields `european_countries.id`, `populated_places.id` and `populated_places.name` are not actually necessary for the given query to work, but I added them for illustration.*

Given the tables above, the query would return the following result:

| name   | counts | population |
| ------ | ------ | ---------- |
| Spain  | 2      | 2100       |
| France | 1      | 3000       |

**How I resolved it:**

* I looked up `ST_Intersect` in the  PostGIS documentation, and found out that it returns TRUE, if "a geometry or geography shares any portion of space" ([see PostGIS documentation](https://postgis.net/docs/ST_Intersects.html)).

## airquality API

* I decided to use python with flask since the microframework seemed a good fit for a quick project like this.
* I wrote some tests using pytest.

**First query: Statistical measurements**

The first query I wrote should return the requested statistical measurement for a given variable for each station. I wrote the following example, then generalized it in the python code to use the parameters provided by the user:

```sql
SELECT station_id, avg(so2)
FROM aasuero.test_airquality_measurements
WHERE timeinstant >= '2017-06-01T00:00:00'
AND timeinstant < '2017-07-01T00:00:00'
GROUP BY station_id
```

**Second query: spatial join**

Now, I needed to add the population of the station to each row, which I can get from `esp_grid_1km_demographic` by looking for the grid cell that includes coordinates of each station.

Therefore, I need to obtain the coordinates of each station. While the table `test_airquality_measurements` has a column `the_geom` that looked promising, the value of this column seems to be `null` for every row.

Therefore, I need to join  `test_airquality_measurements` with `test_airquality_stations`  to obtain the coordinates of each station, and then with `esp_grid_1km_demographic` to obtain the population.

I looked at the PostGIS documentation and found the function `ST_Contains` that seems to do what I need ([see PostGIS documentation](https://postgis.net/docs/manual-3.1/ST_Contains.html)).

I wrote the following example, then generalized it in the python code:

```sql
SELECT s.station_id, g.population, avg(m.so2)
FROM aasuero.test_airquality_stations s
JOIN aasuero.test_airquality_measurements m
ON s.station_id=m.station_id
JOIN aasuero.esp_grid_1km_demographics g
ON ST_Contains(g.the_geom, s.the_geom)
WHERE m.timeinstant >= '2017-06-01T00:00:00'
AND m.timeinstant < '2017-07-01T00:00:00'
GROUP BY s.station_id, s.the_geom, g.population
```

**Third query: Timeseries**

Now, I needed to add the possibility to get the results in hour, day, or week intervals. I did this by truncating the `timeinstany` to the previous hour, day, or week.

I wrote the following example, then generalized it in the python code:

```sql
SELECT s.station_id, g.population, avg(m.so2), date_trunc('hour', timeinstant) as interval_start
FROM aasuero.test_airquality_stations s
JOIN aasuero.test_airquality_measurements m
ON s.station_id=m.station_id
JOIN aasuero.esp_grid_1km_demographics g
ON ST_Contains(g.the_geom, s.the_geom)
WHERE m.timeinstant >= '2017-06-01T00:00:00'
AND m.timeinstant < '2017-07-01T00:00:00'
GROUP BY s.station_id, s.the_geom, g.population, interval_start
```

**Stations filter**

I simply added one more constraint to the query:

```sql
AND m.station_id IN ('aq_jaen', 'aq_salvia', 'aq_nevero')
```

This constraint is added only if the user provides the optional parameter `stations`.

To make sure that I do not make a SQL query with a `station_id` that does not actually exist, I validate the user input first. First, I get the list of 10 stations:

 ```sql
SELECT station_id FROM aasuero.test_airquality_stations
 ```

Then, check that the ones provided by the user in the parameters are in the list returned by the previous statement.

**Geom filter**

First, I needed a way to convert the GeoJSON object provided by the user, to the format understood by PostGIS. I found the `ST_GeomFromGeoJSON` function ([see PostGIS documentation](https://postgis.net/docs/ST_GeomFromGeoJSON.html)).

Then I combined that function with `ST_Intersect` for the following constraint:

```sql
AND ST_Intersects(ST_GeomFromGeoJSON('...'), s.the_geom)
```

(`s` refers to `aasuero.test_airquality_stations` as defined in the query above.)

This constraint is added only if the user provides the optional parameter `geom`.

To catch any invalid GeoJSON objects early, I execute the following query as part of the GET parameter validation:

```sql
SELECT ST_GeomFromGeoJSON('...')
```

If this query returns an error, I show it to the user and do not even execute the complex query that returns the measurements.

**A note on SQL injection**

The SQL queries I send to the CARTO API are constructed by inserting the values provided by the users into String templates. While this is not the approach I would usually choose, I did it for two reasons:

* Since I am not accessing any database directly, I am lacking the usual libraries that allow more secure substitution of variables in SQL queries.
* I only have read-only access to a public data set, therefore no damage can be done by SQL injection.

**How I would implement authentication**

The way that I implemented authentication and access restrictions for similar projects in the past is using tokens:

* An unauthenticated user would only be able to access the endpoint for logging in.
* If the user provides the correct credentials to that endpoint, he would receive a time-limited token in return.
* The user would need to include the token in the request parameters for any subsequent request they perform.
* A middleware component would be executed before the handler for each endpoint. This middleware would identify the user based on the token and check if they have permissions.
* Such a middleware could also be used to log everything a user does for billing purposes.

**Deployment**

I deployed the api on heroku as this platform offers a very quick setup, as well as deployments via git push. It can be found at: `miguel-airquality.herokuapp.com`. Only two endpoints exist:

* `miguel-airquality.herokuapp.com/measurements`
* `miguel-airquality.herokuapp.com/timeseries`

**Tests**

I wrote automated tests for both positive and negative use cases. The tests check the responses returned by the api when accessing the endpoints with different parameters. I did not mock out the CARTO api, that means that my tests could be considered end-to-end tests more than unit tests.
