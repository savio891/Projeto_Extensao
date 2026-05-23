package br.com.faculdade;
import java.io.*;

public class Principal {
    public static void main(String[] args) {
        try{
            String pythonPath = "python";
            String scriptPath = "extrator.py";
            String pdfPath = "";

            ProcessBuilder pb = new ProcessBuilder(pythonPath, scriptPath, pdfPath);
            Process processo = pb.start();

            BufferedReader leitor = new BufferedReader(new InputStreamReader(processo.getInputStream()));
            String linha;
            while((linha = leitor.readLine()) != null) {
                System.out.println("O Python disse: " + linha);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
