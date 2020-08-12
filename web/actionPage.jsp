<%@ page import="java.util.ArrayList" %><%--Specifies the content of this JSP page, i.e. text/html--%>
<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<html>
<head>
    <%-- Following code gives the title to the browser Tab--%>
    <title>Processing</title>
    <%--Following line links the jsp to the respective CSS file for style related changes--%>
    <link rel="stylesheet" type="text/css" href="${pageContext.request.contextPath}actionPage.css">
</head>
<body>
<%--The page heading--%>
<%--add the file name here--%>
<h1>Success!! Thanks for uploading the file!</h1>

<p>The following are the names of all uploaded files:</p>
<% for(String name: (ArrayList<String>)request.getAttribute("uploadedFileName")) { %>
<p> <%=name%> </p>
<%}%>
<%--Following code creates the "Start Processing Now" button--%>
<p>Click on the "Start Processing Now" button to extract data from the uploaded file:</p>
<form action="/resultPage" method="post" enctype="multipart/form-data">
    <input id="startProcessingButton" type="submit" value="Start Processing Now" onclick="handleClick()">
</form>
<%--Creating the Loader in the center in hidden format which becomes visible on click of "Start Processing Now" button--%>
<h2 id="text" hidden="true">File Processing...Please wait...</h2>
<div id="loaderPart" class="loader" hidden="true"></div>
<br>
</body>
<%--The following JavaScript Code controls the visibility of the loader and the accompanying text on click of "Start Processing Now" button--%>
<script type="text/javascript">
    function handleClick()
    {
        document.getElementById('loaderPart').hidden=false;
        document.getElementById('text').hidden=false;
    }
</script>
</html>