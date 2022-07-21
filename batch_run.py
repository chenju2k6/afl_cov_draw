import os
import sys
import time

import multiprocessing 
import subprocess
from multiprocessing.pool import ThreadPool

# g_seed_root = '/home/cju/e2e_data_sampling'

g_cb_bin = 'neuzz_bin'

g_cbs = ['nm','objdump','size','readelf']


g_heads = {'SymSan':'symsan', 'SymCC':'symcc'}

g_cov_root = 'cov_data'
# g_cov_root = '/home/jinghan/cju/ccs_ini3'

g_afl_bin = './afl-fuzz'


g_trials = range(1, 11)


def ensure_dir(dname):
    if not os.path.isdir(dname):
        try:
            os.mkdir(dname, 0o777)
        except OSError as e:
            import errno
            if e.errno != errno.EEXIST:
                raise 



def add_paras(csid):
        if 'readelf' in csid:
            return ['-a', '@@']
        elif 'tcpdump' in csid:
            return ['-R', '@@']
        elif 'strings' in csid:
            return ['-a', '@@']
        elif 'file' in csid:
            return ['@@']
        elif 'objdump' in csid:
            return ['-D', '@@']
        elif 'gzip' in csid:
            return ['-c', '-d', '@@']
        elif 'info2cap' in csid: #infotocap
            return ['-C', '@@']
        elif 'nm' in csid:
            return ['-C', '@@']
        else:
            return ['@@']



def run_afl(cb, label, seq):

    # print 'starting {} {} {}'.format(cb, label, seq)

    my_env = os.environ
    my_env['AFL_NO_AFFINITY'] = '1'
    my_env['AFL_SKIP_CRASHES'] = '1'

    # cb_fp = os.path.join(g_cb_bin, cb)
    # cb_fp = os.path.join(g_init, cb, cb)
    cb_fp = os.path.join(g_cb_bin, cb)

    # init_dir = os.path.join(g_init, cb, 'neuzz_in')
    
    head = g_heads.get(label, None)

    queue_dir = '{}_{}{}'.format(head, cb, seq)

    if head in ['symsan']:
      queue_dir = os.path.join(queue_dir, 'angora', 'queue')
    elif head == 'symcc':
      queue_dir = os.path.join(queue_dir, 'afl-secondary', 'queue')

    #queue_dir = os.path.join(g_seed_root2, queue_dir)

    # queue_dir = os.path.join(g_seed_root, cb, 'neuzz_in')
    
    print(queue_dir)
    if not os.path.exists(queue_dir):
        print 'missing {}'.format(queue_dir)
        return -1

    out_dir = os.path.join(g_cov_root, cb)
    ensure_dir(out_dir)
    out_dir = os.path.join(out_dir, '{}_{}'.format(label, seq))
    ensure_dir(out_dir)

    args = [g_afl_bin]
    args += ['-m', 'none']
    args += ['-t', '2000+']
    args += ['-i', queue_dir]
    args += ['-o', out_dir]
    args += ['--', cb_fp]
    args += add_paras(cb)

    print(args)

    # fd_stdout = open('/dev/null', 'w')

    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=my_env, close_fds=True)
    #proc = subprocess.Popen(args, env=my_env, close_fds=True)
    out, err = proc.communicate()
   #proc.wait()

    print '{} {} {} finished'.format(cb, label, seq)

    return 0



def batch_run():
    thread_pool = ThreadPool(60)

    runners = dict()

    cbs = g_cbs

    labels = ['SymSan', 'SymCC']


    trials = range(1, 4)

    for cb in cbs:
        for label in labels:
            for i in trials:
                print 'scaning {} {} {}'.format(cb, label, i)
                tag = '{}_{}_{}'.format(cb, label, i)
                runners[tag] = thread_pool.apply_async(run_afl, (cb, label, i,))
                time.sleep(1)

    thread_pool.close()
    thread_pool.join()

    for i in sorted(runners.keys()):
        runners[i].get()
        # print '{} finished'.format(i)

    


def main():

    # cb = sys.argv[1]
    # run_afl('nm', 'Z3', '1')
    batch_run()




if __name__ == '__main__':
    main()
