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
<body>

<p>Click on the "Choose File" button to upload a file:</p>

<form action="/action_page" method="post" enctype="multipart/form-data">
  <input type="file" id="myFile" name="filename">
  <input type="submit">
</form>

</body>
</html>
