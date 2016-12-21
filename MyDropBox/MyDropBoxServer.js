/*
 * Universidade Federal de São Carlos - Campus Sorocaba
 * Disciplina: Sistemas Distribuídos
 * 
 * Multicast Totalmente Ordenado 
 *
 * Alunos: 
 * Carolina Pascale Campos            RA: 552100
 * Henrique Manoel de Lima Sebastião  RA: 552259
 *
 * Execução: node MyDropBoxServer.js
 *
 *OBS: Deve existir uma pasta chamada server no mesmo diretorio deste arquivo
 */


const express = require('express');
const fs = require('fs');
const busboy = require('connect-busboy');
const bodyParser = require('body-parser');
const rmdir = require('rmdir');

const myDropBoxServer = {};

//All controls here!
myDropBoxServer.controls = function()
{
	 //functions that will be exported as control functions
	 const controls = {getListFiles,getFile,putFile,removeFile,
							 putDir,removeDir};
	 
	 
	 function _listFiles(path)
	 {
		  const dirContent = [];

		  let content = fs.readdirSync(path);

		  for(let c of content)
		  {
				if(c.endsWith(".TMP"))
					 continue
				
				if(fs.lstatSync(path+"/"+c).isDirectory())
				{
					 const subDir = {};
					 subDir["name"] = c
					 subDir["content"] = _listFiles(path+"/"+c);
					 dirContent.push({"directory": subDir});	
				}
				else
					 dirContent.push({"file":c});
		  }

		  return dirContent;
	 }

	 function _writeObjAsJSON(res, obj)
	 {
		  const objStr =  JSON.stringify(obj,null,2);
		  res.write(objStr);
	 }

	 function getListFiles(req,res)
	 {
		  let content = _listFiles("server");
		  _writeObjAsJSON(res,content);
		  res.end();
	 }

	 function getFile(req,res)
	 {
		  res.download("server/"+req.query.filename);
	 }

	 function putFile(req,res)
	 {
		  function copyFile(fieldname,file,filename)
		  {
				const fstream = fs.createWriteStream('server/' + fieldname+'.TMP');
				
				file.pipe(fstream);
				
				fstream.on('error', err => {
					 console.log("erro no pipe:"+fieldname);
					 const objResponse = {status:"fail"};
					 res.status(400);
					 _writeObjAsJSON(res,objResponse);
					 res.end();
				});

				file.on('end', err => {
					 console.log("arquivo ok "+fieldname);
					 const objResponse = {status:"ok"};
					 _writeObjAsJSON(res,objResponse);
					 fstream.close();
					 fs.renameSync('server/' + fieldname+'.TMP','server/' + fieldname);
					 res.end();
				});

				
		  }
		  
		  req.pipe(req.busboy);
		  console.log(req.body);
		  req.busboy.on('file', copyFile);

		  
	 }

	 function removeDir(req,res)
	 {
		  if(!req.query.dirname)
		  {
				const objResponse = {status:"fail"}
				res.status(400);
				objResponse.errorMsg = "dirname should be informed on url";
				_writeObjAsJSON(res,objResponse);
				res.end();
				return;
		  }
		  
		  const dirName = 'server/'+ req.query.dirname;
		  
		  
		  if (fs.existsSync(dirName))
		  {
				rmdir(dirName, (err, dirs, file)=>
						{
							 const objResponse = {status:"ok"};

							 if(err)
							 {
								  console.log("ERRO ao deletar dir"+err);
								  objResponse.status = "fail";
								  res.status(400);
							 }
							 else
								  console.log("deletado dir ");
							 _writeObjAsJSON(res,objResponse);
							 res.end();
						});
				
		  }
		  else
		  {
				console.log("diretorio pra deletar nao existe");
				const objResponse = {status:"fail"};
				objResponse.errorMsg = "dir not exists";
				res.status(400);
				_writeObjAsJSON(res,objResponse);
				res.end();
		  }
	 }
	 
	 function putDir(req, res)
	 {
		  const objResponse = {status:"fail"};
		  
		  if(!req.body.dirname)
		  {
				res.status(400);
				objResponse.errorMsg = "dirname should be informed into data on request";
				_writeObjAsJSON(res,objResponse);
				res.end();
				return;
		  }
		  
		  const dirName = 'server/'+ req.body.dirname;
		  
		  console.log("debug "+dirName);
		  
		  if (!fs.existsSync(dirName))
		  {
				try
				{
					 fs.mkdirSync(dirName);
					 objResponse.status = "ok"
					 _writeObjAsJSON(res,objResponse);
					 console.log("criado diretorio "+dirName);
					 res.end();
				}
				catch(err)
				{
					 res.status(400);
					 objResponse.errorMsg = "cannot create the directory, check if the path when you trying put directory exists";
					 _writeObjAsJSON(res,objResponse);
					 console.log("falha ao criar diretorio "+dirName);
					 res.end();
				}
				return;
		  }
		  else
				objResponse.status = "nothing";

		  res.status(400);
		  objResponse.errorMsg = "The directory already exists, nothing was made";
		  _writeObjAsJSON(res,objResponse);
		  console.log("diretorio "+dirName+" ja existe");
		  res.end();
		  
	 }

	 function removeFile(req,res)
	 {
		  const objResponse = {status: "fail"};

		  if(!req.query.filename)
		  {
				res.status(400);
				obj.errorMsg = "filename should be informed in url";
				_writeObjAsJSON(res,objResponse);
				res.end();
				return;
		  }
		  try
		  {
				fs.unlinkSync("server/"+req.query.filename);

				objResponse.status = "ok";
				_writeObjAsJSON(res,objResponse);
				res.end();
		  }
		  catch (err)
		  {
				res.status(400);
				_writeObjAsJSON(res,objResponse);
				res.end();
		  }
		  
		  
		  
		  
	 }
	 
	 
	 return controls;
	 
}();

myDropBoxServer.startServer = function()
{
	 //all control maps here!
	 function appMapControls(app)
	 {
		  const control = myDropBoxServer.controls;
		  
		  app.get('/listFiles',control.getListFiles);
		  app.get('/getFile',control.getFile);
		  app.put('/putFile',control.putFile);
		  app.put('/putDir',control.putDir);
		  app.delete('/removeFile',control.removeFile);
		  app.delete('/removeDir',control.removeDir);
	 }

	 function appSetup()
	 {
		  const app = express();
		  app.use(busboy()); 
		  app.use(bodyParser.json());  
		  app.use(bodyParser.urlencoded({
				extended: true
		  }));
		  //app.use(json());
		 // app.use(express.urlencoded()); 
		  appMapControls(app);

		  return app;
	 }

	 function startedMessage(server)
	 {
		  const host = server.address().address
		  const port = server.address().port

		  console.log("App listening at http://%s:%s", host, port);
	 }
	 
	 const app = appSetup();
	 
	 const server = app.listen(8081);

	 startedMessage(server);
	 
}

myDropBoxServer.startServer();
