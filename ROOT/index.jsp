<%--
  Created by IntelliJ IDEA.
  User: sonal
  Date: 6/18/2020
  Time: 1:23 PM
  To change this template use File | Settings | File Templates.
--%>
<%--<%@ page contentType="text/html;charset=UTF-8" language="java" %>--%>
<%--<html>--%>
<%--  <head>--%>
<%--    <title>$Title$</title>--%>
<%--  </head>--%>
<%--  <body>--%>
<%--  $END$--%>
<%--  </body>--%>
<%--</html>--%>
<%@page contentType="text/html" pageEncoding="UTF-8"%>
<!DOCTYPE html>
<html>
<head>
  <title>PDF Table Extractor</title>
  <link rel="stylesheet" type="text/css" href="./welcome.css">
</head>
<h1>Welcome to the Financial Data Extraction Demo</h1>
<br>
<div class="logo">
  <img src="cmuLogo3.png" height="120" width="120">
  <img src="TCSlogo.png" height="100" width="200">
</div>
<br>
<p>Click on the "Choose File" button to upload a file:</p>
<form action="/actionPage" method="post" enctype="multipart/form-data">
  <input type="file" id="myFile" name="filename">
  <input id="submitButton" type="submit" value="Submit">
</form>
</body>
</html>
