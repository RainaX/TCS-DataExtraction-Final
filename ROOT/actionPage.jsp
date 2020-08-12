<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<html>
<head>
    <title>actionPage</title>
    <link rel="stylesheet" type="text/css" href="./actionPage.css">
</head>
<body>
<h1>Success!! Thanks for uploading the file!</h1>
<p>Click on the "Start Processing Now" button to extract data from the uploaded file:</p>
<form action="/resultPage" method="post" enctype="multipart/form-data">
    <input id="startProcessingButton" type="submit" value="Start Processing Now">
</form>

<%--<% if (!(boolean)request.getAttribute("hideLoaderPart")) { %>--%>
<%--document.getElementById('loaderPart').hidden=false;--%>
<%--<% } %>--%>
<div id="loaderPart" hidden="true">
    <h2>File Processing...Please wait...</h2>
    <div class="loader" ></div>
</div>

<br>
</body>
</html>