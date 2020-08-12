import jdk.nashorn.internal.parser.JSONParser;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.rendering.ImageType;
import org.apache.pdfbox.rendering.PDFRenderer;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.*;
import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;
import javax.imageio.ImageIO;
import javax.script.*;
import javax.servlet.RequestDispatcher;
import javax.servlet.ServletException;
import javax.servlet.annotation.MultipartConfig;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.Part;

/**
 * Code Courtesy: https://examples.javacodegeeks.com/enterprise-java/servlet/java-servlet-file-download-file-upload-example/
 * @SonalSingh
 * @XiyuanZhang
 * The following Servlet acts as the controller to integrate the webpage(View) with the Deep Learning Code (python modules).
 * There are four url patterns:
 * /actionPage(processing page), /resultPage(final result page), /viewPage?filename=xxx(download a selected excel file),
 * /downloadAllExcel(download all excel files), /downloadAllJson(download all json files)
 */
@WebServlet(name = "FileUploadServlet",
        urlPatterns = {"/actionPage", "/viewPage", "/resultPage", "/downloadAllExcel", "/downloadAllJson"})
@MultipartConfig(fileSizeThreshold = 1024 * 1024 * 10, maxFileSize = 1024 * 1024 * 30, maxRequestSize = 1024 * 1024 * 50)
public class FileUploadServlet extends HttpServlet{

    private static final long serialVersionUID = 1L;

    /** folder path */
    final String COORDINATES_PATH = "/home/ubuntu/webserver/coordinates";
    final String EXCEL_PATH = "/home/ubuntu/webserver/excel";
    final String OUTPUTIMAGES_PATH = "/home/ubuntu/webserver/outputImages";
    final String OUTPUTSINGLEPAGES_PATH = "/home/ubuntu/webserver/outputSinglePages";
    final String UPLOADEDFILES_PATH = "/home/ubuntu/webserver/uploadedFiles";
    final String PYTHONFILES_PATH = "/home/ubuntu/webserver/pythonFiles";
    final String VIRTUALENVIRONMENT_PATH = "/home/ubuntu/anaconda3/envs/pytorch_p36/bin";
    final String ZIPFILES_PATH = "/home/ubuntu/webserver/zipFiles";
    final String JSONFILES_PATH = "/home/ubuntu/webserver/json";

    /** python file name */
    final String EXTRACT_SINGLE_PAGE_PYTHON_FILE = "Table_Detection_v5.py";
    final String DEEP_LEARNING_PYTHON_FILE = "detection.py";

    /** images resolution */
    final int RESOLUTION = 300;

    @Override
    /**
     * Servlet will reply to HTTP POST requests
     * 1. after user click submit button in index.jsp, upload the file and forward to /actionPage
     * 2. after user click start processing now button in actionPage.jsp, start processing work and
     *    forward to a new page which contains the file list
     */
    protected void doPost(HttpServletRequest request,
                         HttpServletResponse response)
            throws ServletException, IOException {

        /* after user click submit button in index.jsp */
        if (request.getServletPath().equals("/actionPage")){

            /* clean the uploaded files folder */
            cleanFolder(UPLOADEDFILES_PATH);


            File fileUploadDirectory = new File(UPLOADEDFILES_PATH);
            if (!fileUploadDirectory.exists()) {
                fileUploadDirectory.mkdirs();
            }

            String fileName = "";
            /* uploaded file names */
            ArrayList<String> uploadedFileNames = new ArrayList<>();
            for (Part part : request.getParts()) {
                fileName = extractFileName(part);
                /* check whether user uploaded a folder
                *  if yes, the file's name is needed to be extracted from folderName/fileName */
                if (fileName.contains("/")) {
                    fileName = fileName.split("/")[1];
                }
                if (fileName.length() == 0) {
                    continue;
                } else {
                    uploadedFileNames.add(fileName);
                }
                part.write(UPLOADEDFILES_PATH + File.separator + fileName);

            }
            request.setAttribute("uploadedFileName", uploadedFileNames);
            /* forward page to /actionPage.jsp */
            RequestDispatcher dispatcher = request.getRequestDispatcher("/actionPage.jsp");
            dispatcher.forward(request, response);
        }

        /* after user click start processing now button in actionPage.jsp */
        if (request.getServletPath().equals("/resultPage")) {
            /* clean up all things */
            cleanFolder(COORDINATES_PATH);
            cleanFolder(EXCEL_PATH);
            cleanFolder(OUTPUTIMAGES_PATH);
            cleanFolder(OUTPUTSINGLEPAGES_PATH);
            cleanFolder(ZIPFILES_PATH);
            cleanFolder(JSONFILES_PATH);

            /* run the Python code */
            try {
                /* Step1: extract pages that contain the table */
                runPythonCode(EXTRACT_SINGLE_PAGE_PYTHON_FILE);
                /* Step2: convert pdf to images */
                ArrayList<String> fileNamesList = printFileNames();
                convertPDF2Image(fileNamesList);
                /* Step3: use DL model to detect the coordinates */
                runPythonCode(DEEP_LEARNING_PYTHON_FILE);
            } catch (InterruptedException e) {
                e.printStackTrace();
            } catch (ScriptException e) {
                e.printStackTrace();
            }

            fileList(request);
            /* forward to /result.jsp */
            RequestDispatcher dispatcher = request.getRequestDispatcher("/result.jsp");
            dispatcher.forward(request, response);
        }
    }

    @Override
    /**
     * Servlet will reply to HTTP GET requests
     * after user click the file name in /result
     * download the excel sheet to local
     */
    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws IOException {
        /* download a single file*/
        if (request.getServletPath().equals("/viewPage")) {

            /* get the filename from url */
            String fileName = (request.getQueryString()).substring(9);
            fileName = fileName.replaceAll("\\+", " ");
            fileName = fileName.replaceAll("%20", "");

            /* download a single excel sheet file(.xlsx) to local*/
//            response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
            response.addHeader("Content-Disposition", "attachment;filename=" + fileName);
            FileInputStream in = null;
            if (fileName.contains(".xlsx")) {
                in = new FileInputStream(new File(EXCEL_PATH + File.separator + fileName));
            } else if (fileName.contains(".json")) {
                in = new FileInputStream(new File(JSONFILES_PATH + File.separator + fileName));
            }
            OutputStream out = response.getOutputStream();
            byte[] b = new byte[512];
            while ((in.read(b)) != -1) {
                out.write(b);
            }
            out.flush();
            in.close();
            out.close();
        }

        /* zip all excel output files into a zip file and download the zip file to local */
        if (request.getServletPath().equals("/downloadAllExcel")) {
            /* set zipName according to system time */
            String zipName = String.valueOf(new Date().getTime()) + "_excel_files";
            fileToZip(EXCEL_PATH, ZIPFILES_PATH ,zipName);
            response.addHeader("Content-Disposition", "attachment;filename=" + zipName + ".zip");
            FileInputStream in = new FileInputStream(new File(ZIPFILES_PATH + File.separator + zipName + ".zip"));
            OutputStream out = response.getOutputStream();
            byte[] b = new byte[512];
            while ((in.read(b)) != -1) {
                out.write(b);
            }
            out.flush();
            in.close();
            out.close();
        }

        /* zip all json output files into a zip file and download the zip file to local */
        if (request.getServletPath().equals("/downloadAllJson")) {
            /* set zipName according to system time */
            String zipName = String.valueOf(new Date().getTime()) + "_json_files";
            fileToZip(JSONFILES_PATH, ZIPFILES_PATH ,zipName);
            response.addHeader("Content-Disposition", "attachment;filename=" + zipName + ".zip");
            FileInputStream in = new FileInputStream(new File(ZIPFILES_PATH + File.separator + zipName + ".zip"));
            OutputStream out = response.getOutputStream();
            byte[] b = new byte[512];
            while ((in.read(b)) != -1) {
                out.write(b);
            }
            out.flush();
            in.close();
            out.close();
        }
    }

    /**
     * Helper Method #0
     * @param request
     * @throws IOException
     * get the output file list
     * set request's attribute and pass the attribute to result.jsp
     */
    private void fileList(HttpServletRequest request) throws IOException {

        /* generate excel files list*/
        File excelFile = new File(EXCEL_PATH);
        File[] excelFileList = excelFile.listFiles();
        List<String> excelFileNames = new ArrayList<>();
        List<String> excelFileEncodeNames = new ArrayList<>();

        for (File f : excelFileList) {
            String name = f.getName();
            excelFileNames.add(name);
            String encodeName = URLEncoder.encode(name, "utf-8");
            excelFileEncodeNames.add(encodeName);
//            response.getWriter().write("<a href='viewPage?filename=" + encodeName + "'>" + name + "</a><br/>");
        }
        request.setAttribute("excelFileNames", excelFileNames);
        request.setAttribute("excelFileEncodeNames", excelFileEncodeNames);

        /* generate json files list*/
        File jsonFile = new File(JSONFILES_PATH);
        File[] jsonFileList = jsonFile.listFiles();
        List<String> jsonFileNames = new ArrayList<>();
        List<String> jsonFileEncodeNames = new ArrayList<>();

        for (File f : jsonFileList) {
            String name = f.getName();
            jsonFileNames.add(name);
            String encodeName = URLEncoder.encode(name, "utf-8");
            jsonFileEncodeNames.add(encodeName);
//            response.getWriter().write("<a href='viewPage?filename=" + encodeName + "'>" + name + "</a><br/>");
        }
        request.setAttribute("jsonFileNames", jsonFileNames);
        request.setAttribute("jsonFileEncodeNames", jsonFileEncodeNames);
    }

    /**
     * Helper Method #1
     * @param part
     * @return extracted filename
     * This Method Is Used To Read The File Names
     */
    private String extractFileName(Part part) {
        String fileName = "",
                contentDisposition = part.getHeader("content-disposition");
        String[] items = contentDisposition.split(";");
        for (String item : items) {
            if (item.trim().startsWith("filename")) {
                fileName = item.substring(item.indexOf("=") + 2, item.length() - 1);
            }
        }
        return fileName;
    }

    /**
     * Helper Method #2
     * @param functionFileName
     * @throws IOException
     * @throws InterruptedException
     * @throws ScriptException
     * Run the Python code
     * Using Runtime exec
     */
    public void runPythonCode(String functionFileName) throws IOException, InterruptedException, ScriptException {

        try {
            Process proc = null;
            if (functionFileName.equals(EXTRACT_SINGLE_PAGE_PYTHON_FILE)) {
                proc = Runtime.getRuntime().exec("python " + PYTHONFILES_PATH + File.separator + EXTRACT_SINGLE_PAGE_PYTHON_FILE);// run the python file
            } else if (functionFileName.equals(DEEP_LEARNING_PYTHON_FILE)) {
                /* activate virtual environment */
                proc = Runtime.getRuntime().exec(VIRTUALENVIRONMENT_PATH + "/python  " + PYTHONFILES_PATH + File.separator + DEEP_LEARNING_PYTHON_FILE);// run the python file
            }
            BufferedReader in = new BufferedReader(new InputStreamReader(proc.getInputStream()));
            String line = null;
            while ((line = in.readLine()) != null) {
                System.out.println(line);
            }
            in.close();
            proc.waitFor();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    /**
     * Helper Method #3
     * @param fileNamesList
     * This method takes the list of file names provided and converts them from PDF to image format ((.jpg) or (.png)) in order to be used
     * inside the Deep Learning Model.
     */
//    public void convertPDF2Image(ArrayList<String> fileNamesList) {
//    String sourceDir = null ;// "InputPDFs/original.pdf"; // Pdf files are read from this folder
//    String destinationDir = OUTPUTIMAGES_PATH + File.separator; // converted images from pdf document are saved here
//
//        for (String filename : fileNamesList) {
//            sourceDir = OUTPUTSINGLEPAGES_PATH + File.separator + filename;
//            try {
//                File sourceFile = new File(sourceDir);
//                File destinationFile = new File(destinationDir);
//                if (!destinationFile.exists()) {
//                    destinationFile.mkdir();
////                System.out.println("Folder Created -> " + destinationFile.getAbsolutePath());
//                }
//                if (sourceFile.exists()) {
////                System.out.println("Images copied to Folder Location: " + destinationFile.getAbsolutePath());
//                    PDDocument document = PDDocument.load(sourceFile);
//                    PDFRenderer pdfRenderer = new PDFRenderer(document);
//
//                    int numberOfPages = document.getNumberOfPages();
////                System.out.println("Total files to be converting -> " + numberOfPages);
//
//                    String fileName = sourceFile.getName().replace(".pdf", "");
//                    String fileExtension = "png";
//                    /*
//                     * 600 dpi give good image clarity but size of each image is 2x times of 300 dpi.
//                     * Ex:  1. For 300dpi 04-Request-Headers_2.png expected size is 797 KB
//                     *      2. For 600dpi 04-Request-Headers_2.png expected size is 2.42 MB
//                     */
//                    int dpi = 300;// use less dpi for to save more space in harddisk. For professional usage you can use more than 300dpi
//
//                    for (int i = 0; i < numberOfPages; ++i) {
//                        File outPutFile = new File(destinationDir + fileName + "_" + (i + 1) + "." + fileExtension);
//                        BufferedImage bImage = pdfRenderer.renderImageWithDPI(i, dpi, ImageType.RGB);
//                        BufferedImage resized = resize(bImage, 1290, 1020);
//                        ImageIO.write(resized, fileExtension, outPutFile);
//                    }
//
//                    document.close();
////                System.out.println("Converted Images are saved at -> " + destinationFile.getAbsolutePath());
//                } else {
//                    System.err.println(sourceFile.getName() + " File not exists");
//                }
//            } catch (Exception e) {
//                e.printStackTrace();
//            }
//        }
//    }
    public void convertPDF2Image(ArrayList<String> fileNamesList) {
        String sourceDir = null ;// "InputPDFs/original.pdf"; // Pdf files are read from this folder
        String destinationDir = OUTPUTIMAGES_PATH + File.separator; // converted images from pdf document are saved here

        //Get each file name, one by one
        for (String filename : fileNamesList) {
            sourceDir = OUTPUTSINGLEPAGES_PATH + File.separator + filename;
            try {
                File sourceFile = new File(sourceDir);
                File destinationFile = new File(destinationDir);
                if (!destinationFile.exists()) {
                    destinationFile.mkdir(); // create the directory, if doesn't exist
//                    System.out.println("Folder Created -> " + destinationFile.getAbsolutePath());
                }
                if (sourceFile.exists()) {
//                    System.out.println("Images copied to Folder Location: " + destinationFile.getAbsolutePath());
                    PDDocument document = PDDocument.load(sourceFile); //load the source file to be converted
                    PDFRenderer pdfRenderer = new PDFRenderer(document);

                    int numberOfPages = document.getNumberOfPages();
//                    System.out.println("Total files to be converting -> " + numberOfPages);

                    String fileName = sourceFile.getName().replace(".pdf", "");
                    String fileExtension = "jpg";
                    /*
                     * 600 dpi give good image clarity but size of each image is 2x times of 300 dpi.
                     * Ex:  1. For 300dpi 04-Request-Headers_2.png expected size is 797 KB
                     *      2. For 600dpi 04-Request-Headers_2.png expected size is 2.42 MB
                     */
                    int dpi = RESOLUTION;// use less dpi for to save more space in hard disk. For professional usage you can use more than 300dpi

                    // For each page in the document, render the image with provided dpi configurations and write to the output file location
                    for (int i = 0; i < numberOfPages; ++i) {
                        File outPutFile = new File(destinationDir + fileName + "_" + (i + 1) + "." + fileExtension);
                        BufferedImage bImage = pdfRenderer.renderImageWithDPI(i, dpi, ImageType.RGB);
                        ImageIO.write(bImage, fileExtension, outPutFile);
                    }
                    document.close(); //close the document
//                    System.out.println("Converted Images are saved at -> " + destinationFile.getAbsolutePath());
                } else {
                    //Error thrown if the file not found
                    System.err.println(sourceFile.getName() + " File not exists");
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

    /**
     * Helper Method #4
     * @return ArrayList<String> fileNameList
     * This method returns the list of file names(here, page Names) which contains the names of all the PDF pages that contain
     * tables in order to be converted to image for the Deep Learning model.
     */
    ArrayList<String> printFileNames(){
        ArrayList<String> fileNamesList= new ArrayList<>();
        File file = new File(OUTPUTSINGLEPAGES_PATH + File.separator);
        File[] files = file.listFiles();
        for(File f: files){
            System.out.println(f.getName());
            fileNamesList.add(f.getName());
        }
        System.out.println(fileNamesList);
        return fileNamesList;
    }

    /**
     * Helper Method #5
     * convert .jpg to .png
     * Courtesy: https://memorynotfound.com/java-resize-image-fixed-width-height-example/
     * This method resizes the image provided according to the input parameters
     * @param img
     * @param height
     * @param width
     * @return
     */
    private static BufferedImage resize(BufferedImage img, int height, int width) {
        /**
         *     Image.SCALE_DEFAULT – uses the default image-scaling algorithm.
         *     Image.SCALE_FAST – uses an image-scaling algorithm that gives higher priority to scaling speed than smoothness of the scaled image.
         *     Image.SCALE_SMOOTH – uses an image-scaling algorithm that gives higher priority to image smoothness than scaling speed.
         *     Image.SCALE_REPLICATE – use the image scaling algorithm embodied in the ReplicateScaleFilter class.
         *     Image.SCALE_AREA_AVERAGING – uses the area averaging image scaling algorithm.
         */
        Image tmp = img.getScaledInstance(width, height, Image.SCALE_DEFAULT);
        BufferedImage resized = new BufferedImage(width, height, BufferedImage.TYPE_INT_ARGB);
        Graphics2D g2d = resized.createGraphics();
        g2d.drawImage(tmp, 0, 0, null);
        g2d.dispose();
        return resized;
    }

    /**
     * Helper Method #6
     * @param path
     * clean the folder according to the path
     */
    private void cleanFolder(String path) {
        File file = new File(path);
        String[] childFilePath = file.list();
        for (String p : childFilePath){
            File childFile = new File(file.getAbsoluteFile() + File.separator + p);
            childFile.delete();
        }
    }

    /**
     * Helper Method #7
     * @param sourceFilePath : the path of excel output or json output
     * @param zipFilePath : the path of zip file
     * @param fileName : zip file name
     * Pack the source file stored in the sourceFilePath directory into a zip file named fileName and store it in the zipFilePath path
     */
    public static boolean fileToZip(String sourceFilePath,String zipFilePath,String fileName){
        boolean flag = false;
        File sourceFile = new File(sourceFilePath);
        FileInputStream fis = null;
        BufferedInputStream bis = null;
        FileOutputStream fos = null;
        ZipOutputStream zos = null;

        if(sourceFile.exists() == false){
            sourceFile.mkdir();
        }
        try {
            File zipFile = new File(zipFilePath + "/" + fileName +".zip");
            if(zipFile.exists()){
            }else{
                File[] sourceFiles = sourceFile.listFiles();
                if(null == sourceFiles || sourceFiles.length<1){
                }else{
                    fos = new FileOutputStream(zipFile);
                    zos = new ZipOutputStream(new BufferedOutputStream(fos));
                    byte[] bufs = new byte[1024*10];
                    for(int i=0;i<sourceFiles.length;i++){
                        // create zip entry
                        ZipEntry zipEntry = new ZipEntry(sourceFiles[i].getName());
                        zos.putNextEntry(zipEntry);
                        // write files into zip
                        fis = new FileInputStream(sourceFiles[i]);
                        bis = new BufferedInputStream(fis, 1024*10);
                        int read = 0;
                        while((read=bis.read(bufs, 0, 1024*10)) != -1){
                            zos.write(bufs,0,read);
                        }
                    }
                    flag = true;
                }
            }
        } catch (FileNotFoundException e) {
            e.printStackTrace();
            throw new RuntimeException(e);
        } catch (IOException e) {
            e.printStackTrace();
            throw new RuntimeException(e);
        } finally{
            try {
                if(null != bis) bis.close();
                if(null != zos) zos.close();
            } catch (IOException e) {
                e.printStackTrace();
                throw new RuntimeException(e);
            }
        }
        return flag;
    }
}
