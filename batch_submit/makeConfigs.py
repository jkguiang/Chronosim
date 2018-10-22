import glob, os, subprocess

tag = "test_v1"

outdir = "/hadoop/cms/store/user/jguiang/chronosim/{0}".format(tag)

fout = open("configs/config_{0}.cmd".format(tag), 'w')

username = os.environ["USER"]
x509file = subprocess.check_output(["find","/tmp/", "-maxdepth", "1", "-type", "f", "-user", username, "-regex", "^.*x509.*$"])
os.system("mkdir -p /data/tmp/{0}/condor_job_logs/chronosim/".format(username))
os.system("mkdir -p /data/tmp/{0}/condor_submit_logs/chronosim/".format(username))

fout.write("""
universe=Vanilla
when_to_transfer_output = ON_EXIT
transfer_input_files=wrapper.sh, package.tar.xz
+DESIRED_Sites="T2_US_UCSD"
+remote_DESIRED_Sites="T2_US_UCSD"
+Owner = undefined
log=/data/tmp/{0}/condor_submit_logs/chronosim/condor_12_01_16.log
output=/data/tmp/{0}/condor_job_logs/chronosim/1e.$(Cluster).$(Process).out
error =/data/tmp/{0}/condor_job_logs/chronosim/1e.$(Cluster).$(Process).err
notification=Never
x509userproxy={1}

""".format(username, x509file))

files = glob.glob("/hadoop/cms/store/user/bemarsh/LGAD/traj_inputs_for_jonathan/{0}/*.txt".format(tag))
jobid = 0
for f in files:
    jobid = (f.split("_")[-1]).split(".")[0]
    fout.write("executable=wrapper.sh\n")
    fout.write("transfer_executable=True\n")
    fout.write("arguments={0} {1} {2}\n".format(jobid, tag, outdir))
    fout.write("queue\n\n")


fout.close()
