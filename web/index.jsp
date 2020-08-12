<%--Specifies the content of this JSP page, i.e. text/html--%>
<%@page contentType="text/html" pageEncoding="UTF-8"%>
<!DOCTYPE html>
<html>
<head>
<%-- Following code gives the title to the browser Tab--%>
  <title>PDF Table Extractor</title>
  <%--Following line links the jsp to the respective CSS file for style related changes--%>
  <link rel="stylesheet" type="text/css" href="./welcome.css">
</head>
<%--The page heading--%>
<h1>Welcome to the Financial Data Extraction</h1>
<br>
<%--Adding the images for logo of CMU and TCS--%>
<div class="logo">
  <img src="cmuLogo3.png" height="120" width="120">
  <img src="TCSlogo.png" height="100" width="200">
</div>
<br>
<%--Following code creates the file upload Browse and Submit buttons respectively--%>
<p>Click on the "Choose File" button to upload a file or "Choose Folder" button to upload a folder:</p>
<form action="/actionPage" method="post" enctype="multipart/form-data">
<%--  The button designed for uploading a single file--%>
  <input type="button" id="myFileButton" value="Choose File" onclick="document.getElementById('myFile').click();" />
  <input type="file" id="myFile" name="filename" style="display:none;">
<%--  The button designed for uploading a folder--%>
  <input type="button" id="myFileFolderButton" value="Choose Folder" onclick="document.getElementById('myFileFolder').click();" />
  <input type="file" id="myFileFolder" name="fileFolder" style="display:none;" webkitdirectory mozdirectory><br><br>
  <input id="submitButton" type="submit" value="Upload">
</form>
</body>
</html>
