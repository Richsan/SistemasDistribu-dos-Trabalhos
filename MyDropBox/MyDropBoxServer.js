const express = require('express');
const fs = require('fs');

const myDropBoxServer = {};

myDropBoxServer.listFiles = function (path)
{
	 const dirContent = [];

	 const content = fs.readdirSync(path);

	 for(let c of content)
	 {
		  if(fs.lstatSync(path+"/"+c).isDirectory())
		  {
				const subDir = {};
				subDir["name"] = c
				subDir["content"] = myDropBoxServer.listFiles(path+"/"+c);
				dirContent.push({"directory": subDir});	
		  }
		  else
				dirContent.push({"file":c});
	 }

	 return dirContent;
}

myDropBoxServer.getListFiles = function(req,res)
{
	 let content = myDropBoxServer.listFiles("server");
	 let dirFilesStr = JSON.stringify(content,null,2);
	 res.write(dirFilesStr);
	 res.end();
}



myDropBoxServer.startServer = function()
{
	 //all controls here!
	 function appSetup(app)
	 {
		  app.get('/listFiles',myDropBoxServer.getListFiles);

	 }

	 function startedMessage(server)
	 {
		  const host = server.address().address
		  const port = server.address().port

		  console.log("App listening at http://%s:%s", host, port);
	 }
	 
	 const app = express();
	 appSetup(app);

	 const server = app.listen(8081);

	 startedMessage(server);
	 
}

myDropBoxServer.startServer();
