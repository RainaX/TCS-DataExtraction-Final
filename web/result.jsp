<%@ page import="java.util.ArrayList" %>
<%--Specifies the content of this JSP page, i.e. text/html--%>
<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<html>
<head>
    <%-- Following code gives the title to the browser Tab--%>
    <title>Result</title>
        <%--Following line links the jsp to the respective CSS file for style related changes--%>
    <link rel="stylesheet" type="text/css" href="./result.css">
</head>
<body>
<%--The page heading--%>
<h1>Processing completed</h1>
<p>Choose file format to download:</p>
<%--The following JavaScript Code renders the downloadable filenames one by one using for loop from the list--%>
<br>
<div class="options">
    <button class="button" onclick="handleClickExcel()">Excel</button>
    <button class="button" onclick="handleClickJSON()">JSON</button>
</div>
<br>
<br>
<script type="text/javascript">
    function handleClickJSON()
    {
        document.getElementById('jsonForm').hidden=false;
        document.getElementById('downloadAllJson').hidden=false;
        document.getElementById('excelForm').hidden=true;
        document.getElementById('downloadAllExcel').hidden=true;
    }
    function handleClickExcel()
    {
        document.getElementById('excelForm').hidden=false;
        document.getElementById('downloadAllExcel').hidden=false;
        document.getElementById('jsonForm').hidden=true;
        document.getElementById('downloadAllJson').hidden=true;

    }
</script>
<%--json output part--%>
<form id="jsonForm" hidden=true>
    <p>Below is the file list that we generated, click filename to download the output or click "Download All" button to download all files:<p>
        <% for(int i = 0; i < ((ArrayList<String>)request.getAttribute("jsonFileNames")).size(); i++) { %>
    <a href="viewPage?filename= <%=((ArrayList) request.getAttribute("jsonFileEncodeNames")).get(i)%>"> <%=((ArrayList<String>) request.getAttribute("jsonFileNames")).get(i)%> </a><br/>
        <%}%>
</form>
<form action="/downloadAllJson" method="get" enctype="multipart/form-data" hidden="true" id="downloadAllJson">
    <%--  The button designed for downloading all files to local--%>
    <button class="button">Download All</button>
</form>

<%--excel output part--%>
<form id="excelForm" hidden="true">
    <p>Below is the file list that we generated, click filename to download the output or click "Download All" button to download all files:<p>
    <% for(int i = 0; i < ((ArrayList<String>)request.getAttribute("excelFileNames")).size(); i++) { %>
    <a href="viewPage?filename= <%=((ArrayList) request.getAttribute("excelFileEncodeNames")).get(i)%>"> <%=((ArrayList<String>) request.getAttribute("excelFileNames")).get(i)%> </a><br/>
    <%}%>
</form>
<form action="/downloadAllExcel" method="get" enctype="multipart/form-data" hidden="true" id="downloadAllExcel">
    <%--  The button designed for downloading all files to local--%>
    <button class="button">Download All</button>
</form>
</body>
</html>