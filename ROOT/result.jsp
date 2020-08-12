<%@ page import="java.util.ArrayList" %><%--
  Created by IntelliJ IDEA.
  User: sonal
  Date: 6/22/2020
  Time: 8:19 AM
  To change this template use File | Settings | File Templates.
--%>
<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<html>
<head>
    <title>Result</title>
    <link rel="stylesheet" type="text/css" href="./result.css">
</head>
<body>
<h1>Processing completed</h1>
<br>
<%--<p>Choose file format to download:</p>--%>
<%--<div class="options">--%>
<%--    <button class="button">Excel</button>--%>
<%--    <button class="button">JSON</button>--%>
<%--</div>--%>
<form>
    <p id="excelText" >Below is the file list that we generated, click filename to download the output:<p>
    <% for(int i = 0; i < ((ArrayList<String>)request.getAttribute("names")).size(); i++) { %>
    <a href="viewPage?filename= <%=((ArrayList) request.getAttribute("encodeNames")).get(i)%>"> <%=((ArrayList<String>) request.getAttribute("names")).get(i)%> </a><br/>
    <%}%>
    <p id="jsonText" >
        <textarea>
        {
            color: "cyan",
            value: "#0ff"
        }
        </textarea>
    </p>
</form>
</body>
</html>