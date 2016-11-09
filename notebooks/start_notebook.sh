echo "To view the notebook locally, run:"
echo "ssh -L 8888:$HOSTNAME:8888 hpc-login1.hpc.nrel.gov"
echo "Then open your browser to http://localhost:8888/"
jupyter notebook --no-browser --ip 0.0.0.0

