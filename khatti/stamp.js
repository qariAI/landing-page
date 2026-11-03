/* Portable in both a standalone CommonJS folder and this ESM source checkout.
 * Run before every upload: node stamp.js
 * Any missing asset or unrecognised worker marker fails the release step.
 */
(async()=>{
 const fs=await import('node:fs/promises'),path=await import('node:path'),crypto=await import('node:crypto');
 const folder=path.dirname(path.resolve(process.argv[1]));
 const files=['index.html','pwa.js','manifest.webmanifest','icons/icon-192.png','icons/icon-512.png','icons/apple-touch-icon-180.png'];
 const swPath=path.join(folder,'sw.js'),worker=await fs.readFile(swPath,'utf8'),marker=/const CACHE=FAMILY\+'[0-9a-f]{12}';/g;
 if((worker.match(marker)||[]).length!==1)throw Error('Worker cache marker is missing or ambiguous. No files were changed.');
 const hash=crypto.createHash('sha256');
 for(const name of files){hash.update(name+'\0');hash.update(await fs.readFile(path.join(folder,name)));hash.update('\0');}
 // Worker logic changes also get their own cache, without hashing the stamp itself.
 hash.update(worker.replace(marker,"const CACHE=FAMILY+'000000000000';"));
 const id=hash.digest('hex').slice(0,12),next=worker.replace(marker,"const CACHE=FAMILY+'"+id+"';");
 if(next!==worker)await fs.writeFile(swPath,next);
 process.stdout.write('stamped '+id+'\n');
})().catch(error=>{process.stderr.write('Release stamp failed: '+error.message+'\n');process.exitCode=1;});
