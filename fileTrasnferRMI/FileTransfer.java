/*
* Universidade Federal de São Carlos - Campus Sorocaba
 * Disciplina: Sistemas Distribuídos
 * 
 * Upload de Arquivo com RMI
 *
 * Alunos: 
 * Carolina Pascale Campos            RA: 552100
 * Henrique Manoel de Lima Sebastião  RA: 552259
 *
 * Compilação: javac FileTransfer.java RemoteFileChunk.java Server.java Client.java
 *
 * Execução (Servidor Windows): java Server 
 * Execução (Cliente): java Client host arquivo
 * OBS: Garanta que antes de executar o servidor, exista um diretório 
 *		chamado "serverDir" na mesma pasta que o Server.class
*/

import java.rmi.Remote;
import java.rmi.RemoteException;

public interface FileTransfer extends Remote {

	String sendFile(RemoteFileChunk file) throws RemoteException;

}
