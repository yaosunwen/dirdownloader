# dirdownloader

1. start python http server
   
   <code>python -m http.server -d ~/shares 80</code>
   
1. download files from server
   
   <code>dirdownloader.py --url http://127.0.0.1/ --output ~/download</code>
