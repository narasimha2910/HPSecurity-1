This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.<br>
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.<br>
You will also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.<br>
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.<br>
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.<br>
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

## Database Schema

mysql> use data_center_security
Database changed
mysql> show tables;
+--------------------------------+
| Tables_in_data_center_security |
+--------------------------------+
| images_map                     |
| videos_map                     |
+--------------------------------+
2 rows in set (0.01 sec)

mysql> desc images_map
    -> ;
+-----------+-------------+------+-----+---------+-------+
| Field     | Type        | Null | Key | Default | Extra |
+-----------+-------------+------+-----+---------+-------+
| id        | int(3)      | NO   | PRI | NULL    |       |
| name      | varchar(40) | YES  |     | NULL    |       |
| timestamp | varchar(30) | YES  |     | NULL    |       |
+-----------+-------------+------+-----+---------+-------+
3 rows in set (0.01 sec)

mysql> desc videos_map;
+-----------+-------------+------+-----+---------+-------+
| Field     | Type        | Null | Key | Default | Extra |
+-----------+-------------+------+-----+---------+-------+
| id        | int(3)      | NO   | PRI | NULL    |       |
| name      | varchar(40) | YES  |     | NULL    |       |
| timestamp | varchar(30) | YES  |     | NULL    |       |
+-----------+-------------+------+-----+---------+-------+
3 rows in set (0.01 sec)

mysql> show * from images_map;
ERROR 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '* from images_map' at line 1
mysql>
mysql> select * from images_map;
+----+-------+-------------------+
| id | name  | timestamp         |
+----+-------+-------------------+
|  1 | 1.jpg | 01-01-19 10:48:53 |
|  2 | 2.jpg | 09-01-19 12:23:33 |
|  3 | 3.jpg | 11-01-19 13:25:06 |
|  4 | 4.jpg | 14-01-19 14:06:56 |
+----+-------+-------------------+
4 rows in set (0.03 sec)

mysql> select * from videos_map;
+----+-------+-------------------+
| id | name  | timestamp         |
+----+-------+-------------------+
|  1 | 1.mp4 | 01-01-19 10:48:53 |
|  2 | 2.mp4 | 09-01-19 12:23:33 |
|  3 | 3.mp4 | 11-01-19 13:25:06 |
+----+-------+-------------------+
3 rows in set (0.01 sec)

mysql>

**Note: this is a one-way operation. Once you `eject`, you can???t go back!**

If you aren???t satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (Webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you???re on your own.

You don???t have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn???t feel obligated to use this feature. However we understand that this tool wouldn???t be useful if you couldn???t customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: https://facebook.github.io/create-react-app/docs/code-splitting

### Analyzing the Bundle Size

This section has moved here: https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size

### Making a Progressive Web App

This section has moved here: https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app

### Advanced Configuration

This section has moved here: https://facebook.github.io/create-react-app/docs/advanced-configuration

### Deployment

This section has moved here: https://facebook.github.io/create-react-app/docs/deployment

### `npm run build` fails to minify

This section has moved here: https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify
