const express = require('express');
const fs = require('fs');
const gutil = require('gulp-util');

const myDropBoxServer = {};

myDropBoxServer.listFiles = function (path)
{
   const dirContent = [];

   const content = fs.readdirSync(path);

   for(let c of content)
   {
      if(fs.lstatSync(path + '/' + c).isDirectory())
      {
        const subDir = {};
        subDir['name'] = c
        subDir['content'] = myDropBoxServer.listFiles(path + '/' + c);
        dirContent.push({'directory': subDir});
      }
      else
        dirContent.push({'file': c});
   }

   return dirContent;

}

	myDropBoxServer.delete = (file) => {

		const path = `./server/${file}`;
		const exists = fs.existsSync(path);

		if (exists) {
			console.log(gutil.colors.green('File exists. Deleting now ...'));
		  fs.unlink(path);
		}
		else {
		  console.log(gutil.colors.red('File not found, so not deleting.'));
		};

	}

myDropBoxServer.getListFiles = function(req,res)
{
   let content = myDropBoxServer.listFiles('server');
   let dirFilesStr = JSON.stringify(content, null, 2);
   res.write(dirFilesStr);
   res.end();
}

myDropBoxServer.deleteFile = (req, res) => {

	let content = myDropBoxServer.listFiles('server');
	myDropBoxServer.delete('oi.txt');
  let dirFilesStr = JSON.stringify('oi.txt', null, 2);
  res.write(dirFilesStr);
  res.end();
}



myDropBoxServer.startServer = function()
{
   //all controls here!
   function appSetup(app)
   {
      app.get('/listFiles',myDropBoxServer.getListFiles);
      app.get('/deleteFile', myDropBoxServer.deleteFile);
   }

   function startedMessage(server)
   {
      const { address, port } = server.address();

      console.log(`App listening at http://${address}:${port}`);
   }

   const app = express();
   appSetup(app);

   const server = app.listen(8081);

   startedMessage(server);

}

myDropBoxServer.startServer();