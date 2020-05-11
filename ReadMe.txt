1. Copy the p2mpclient.py, p2mpserver.py2 and input file to the same location
2) Run the p2mpserver.py with the port number, output file name and loss 
   probability as command line arguments
   eg: python p2mpserver.py 7735 output.txt 0.05
3. Run the p2mpclient.py with servers, port number, output filename
   and MSS as command line arguments
   eg: python p2mpserver.py 127.0.0.1 7735 input.txt 600

