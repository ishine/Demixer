import sys
sys.path.append("..")
import os
import matplotlib.pyplot as plt
import numpy as np
from util.wave_util import WaveHandler
from pydub import AudioSegment
from config.mainConfig import Config
from models import spleeter
import torch
from util.wave_util import save_pickle,load_pickle

datahub_root = "/home/disk2/internship_anytime/liuhaohe/datasets/"

musdb_test_pth = datahub_root+"musdb18hq/test/"
musdb_train_pth = datahub_root+"musdb18hq/train/"

def analysis_cache():
    fname = Config.project_root+"dataloader/wavenet/temp"
    with open(fname,'r') as f:
        line = f.readline().strip().split()
    for i in range(len(line)):
        line[i] = int(line[i])
    smooth = 10
    smoothed = []
    for start in range(len(line[smooth:])):
        smoothed.append(sum(line[start:start+smooth])/smooth)
    plt.figure(figsize=(10,5))
    smoothed = smoothed[:3000]
    l1, = plt.plot(smoothed,linewidth = 1)
    l2, = plt.plot(np.zeros((len(smoothed),)),linewidth = 1)
    plt.legend([l1,l2],["cached","without cache"],loc = 'upper right')
    plt.title("Hit rate increases during training(150 songs' cache)")
    plt.savefig("hit_rate.png")

def write_list(l,fname):
    with open(fname,'w') as f:
        for each in l:
            f.write(each+"\n")

def Song_data():
    dir = Config.datahub_root+"seg_song_data/"
    res = []
    for cnt,fname in enumerate(os.listdir(dir)):
        res.append(dir+fname)
    write_list(res,Config.datahub_root+"song_vocal_data_44_1.txt")

def seg_data():
    wh = WaveHandler()
    dir = Config.datahub_root+"song/441_song_data/"
    seg_dir = Config.datahub_root+"song/seg_song_data/"
    for cnt,fname in enumerate(os.listdir(dir)):
        print("Doing segmentation on ",fname+"...")
        unseg_f = dir+fname
        data = wh.read_wave(unseg_f, channel=2)
        length = data.shape[0]
        for start in np.linspace(0,0.95,20):
            seg_data = data[int(start*length):int((start+0.05)*length)]
            wh.save_wave(seg_data,seg_dir+fname.split('.')[-2]+"_"+str('%.2f' % start)+".wav",channels=2)

def pure_music():
    path = Config.datahub_root+"pure_music/"
    pth_name = [path+each for each in os.listdir(path)]
    log = []
    for cnt,each in enumerate(pth_name):
        log.append(each+" -> "+path+"pure_music_"+str(cnt))
        os.rename(each,path+"pure_music_"+str(cnt))
    write_list(log,path+"readme")

def list_and_save_folder(path,save_path):
    if(not path[-1] == '/'):
        raise ValueError("Error: Path should end with / ")
    files = os.listdir(path)
    log = []
    for cnt,each in enumerate(files):
        log.append(path+each)
    write_list(log,save_path)

def plot2wav(a,b):
    plt.figure(figsize=(20,4))
    plt.subplot(211)
    plt.plot(a,linewidth = 0.5)
    plt.subplot(212)
    plt.plot(b,linewidth = 0.5)
    plt.savefig("temp.png")

# delete_unproper_training_data("/home/disk2/internship_anytime/liuhaohe/datasets/pure_music_wav/pure_music_7/")
def delete_unproper_training_data(path):
    if (not path[-1] == '/'):
        raise ValueError("Error: path should end with /")
    wh = WaveHandler()
    files = os.listdir(path)
    for cnt,each in enumerate(files):
        file_pth = path+each
        if(file_pth.split('.')[-1] == 'wav'):
            judge = wh.get_channels_sampwidth_and_sample_rate(file_pth)
            if(not judge[0]):
                print(each,"Unproper! params:",judge[1])
                os.remove(file_pth)


def plot3wav(a,b,c):
    import matplotlib.pyplot as plt
    plt.figure(figsize=(30,6))
    plt.subplot(311)
    plt.plot(a,linewidth = 1)
    plt.subplot(312)
    plt.plot(b,linewidth = 1)
    plt.subplot(313)
    plt.plot(c,linewidth = 1)
    plt.savefig("commmmm1.png")

def trans_mp3_folder_to_wav(root_path,save_folder):
    if(not save_folder[-1] == '/' or not root_path[-1] == '/'):
        raise ValueError("Error: path should end with /")
    if(not os.path.exists(root_path)):
        raise ValueError(root_path+" does not exist!")
    if(not os.path.exists(save_folder)):
        os.mkdir(save_folder)
    for cnt,each in enumerate(os.listdir(root_path)):
        if(each.split('.')[-1] == 'mp3'):
            try:
                trans_mp3_to_wav(root_path+each,save_folder)
            except:
                print("Failed to transfer: "+each)
        if(cnt % 20 == 0):
            print(cnt,"files finished")

def trans_mp3_to_wav(filepath:str,savepath:str):
    if(not savepath[-1] == '/'):
        raise ValueError("Error: savepath should end with /")
    name = filepath.split('.')[-2].split('/')[-1]
    song = AudioSegment.from_mp3(filepath)
    song.export(savepath+name+".wav", format="wav")

def get_total_time_in_folder(path):
    if(not path[-1] == '/'):
        raise ValueError("Error: path should end with /")
    wh = WaveHandler()
    total_time = 0
    for cnt,file in enumerate(os.listdir(path)):
        total_time += wh.get_duration(path+file)
    print("total: ")
    print(total_time,"s")
    print(total_time/60,"min")
    print(total_time/3600,"h")

def readList(fname):
    result = []
    with open(fname,"r") as f:
        for each in f.readlines():
            each = each.strip('\n')
            result.append(each)
    return result

def get_total_time_in_txt(txtpath):
    wh = WaveHandler()
    cnt = 0
    files = readList(txtpath)
    total_time = 0
    for file in files:
        try:
            total_time += wh.get_duration(file)
            cnt += 1
        except:
            print("error:",file)

    # print(total_time,"s")
    # print(total_time/60,"min")
    print(txtpath.split('/')[-1].split('.')[-2],",",str(total_time/3600)+"h,",cnt,", "+txtpath)
    return total_time/3600,cnt


def netease_filter(root_path:str,save_path:str):
    if(root_path[-1]!='/'):
        raise ValueError("Error: Path should end with /")
    list_names = os.listdir(root_path)
    for each in list_names:
        list_path = root_path+each+"/"
        save_list_path = save_path+each+"/"
        txt_path = Config.datahub_root+"datahub/" + each + ".txt"
        if (not os.path.exists(list_path)):
            continue
        if (not os.path.exists(save_list_path)):
            trans_mp3_folder_to_wav(list_path,save_list_path)
        delete_unproper_training_data(save_list_path)
        list_and_save_folder(save_list_path,txt_path)
        print(each,"Time statistic")
        get_total_time_in_txt(txt_path)
        # print("Done!")
        print("")

def rename_musdb():
    musdb_test = Config.datahub_root+"musdb18hq/test/"
    musdb_train = Config.datahub_root+"musdb18hq/train/"

    for each in os.listdir(musdb_test):
        os.rename(musdb_test+each+"/mixed.wav",musdb_test+each+"/background.wav")
    for each in os.listdir(musdb_train):
        os.rename(musdb_train+each+"/mixed.wav",musdb_train+each+"/background.wav")

def construct_musdb():
    musdb_test = Config.datahub_root+"musdb18hq/test/"
    musdb_train = Config.datahub_root+"musdb18hq/train/"
    test_vocal = []
    train_vocal = []
    train_background = []
    test_background = []
    for each in os.listdir(musdb_test):
        test_vocal.append(musdb_test+each+"/vocals.wav")
        test_background.append(musdb_test+each+"/background.wav")
    for each in os.listdir(musdb_train):
        train_vocal.append(musdb_train+each+"/vocals.wav")
        train_background.append(musdb_train+each+"/background.wav")
    write_list(test_vocal,Config.musdb_test_vocal)
    write_list(train_vocal,Config.musdb_train_vocal)
    write_list(train_background,Config.musdb_train_background)
    write_list(test_background,Config.musdb_test_background)

def construct_song():
    song = Config.datahub_root+"song_data/"
    song_dir = []
    for each in os.listdir(song):
        delete_unproper_training_data(song+"/")
        song_dir.append(song+"/"+each)
    write_list(song_dir,Config.datahub_root+"datahub/song_vocal_data_44_1.txt")

def construct_kpop():
    song = Config.datahub_root+"pure_vocal/k_pop"
    song_dir = []
    for each in os.listdir(song):
        delete_unproper_training_data(song+"/")
        song_dir.append(song+"/"+each)
    write_list(song_dir,Config.datahub_root+"datahub/k_pop.txt")

def report_data():
    root = Config.datahub_root+"datahub/"
    for each in os.listdir(root):
        get_total_time_in_txt(root+each)

def merge_musdb():
    for each in os.listdir(Config.musdb_test_pth):
        test_dir = Config.musdb_test_pth+each+"/"
        os.system("sox -m "+test_dir+"vocals.wav "+test_dir+"background.wav "+test_dir+"combined.wav")
        print("ok1")
    for each in os.listdir(Config.musdb_train_pth):
        train_dir = Config.musdb_train_pth + each + "/"
        os.system("sox -m "+train_dir+"vocals.wav "+train_dir+"background.wav "+train_dir+"combined.wav")
        print("ok2")

# spleeter separate -i combined.wav -p spleeter:2stems -o output
def spleet_musdb():
    output_test_pth = Config.datahub_root+"musdb18hq/spleeter_out/test/"
    output_train_pth = Config.datahub_root+"musdb18hq/spleeter_out/train/"

    for each in os.listdir(musdb_test_pth):
        print(each)
        if (os.path.exists(output_test_pth + each + "/" + "output/combined/vocals.wav")
                and os.path.exists(output_test_pth + each + "/" + "output/combined/accompaniment.wav")):
            continue
        test_dir = musdb_test_pth+each+"/"
        os.system("spleeter separate -i " + test_dir + "combined.wav" + " -p spleeter:2stems -o "
                  + output_test_pth + each + "/" + "output")
    for each in os.listdir(musdb_train_pth):
        print(each)
        if(os.path.exists(output_train_pth+each+"/"+"output/combined/vocals.wav")
                and os.path.exists(output_train_pth+each+"/"+"output/combined/accompaniment.wav")):
            continue
        train_dir = musdb_train_pth + each + "/"
        os.system("spleeter separate -i "+train_dir+"combined.wav"+" -p spleeter:2stems -o "
                  +output_train_pth+each+"/"+"output")

def netease_filter(root_path:str,save_path:str):
    if(root_path[-1]!='/'):
        raise ValueError("Error: Path should end with /")
    list_names = os.listdir(root_path)
    for each in list_names:
        list_path = root_path+each+"/"
        save_list_path = save_path+each+"/"
        txt_path = Config.datahub_root+"datahub/" + each + ".txt"
        if (not os.path.exists(list_path)):
            continue
        if (not os.path.exists(save_list_path)):
            trans_mp3_folder_to_wav(list_path,save_list_path)
        delete_unproper_training_data(save_list_path)
        list_and_save_folder(save_list_path,txt_path)
        print(each,"Time statistic")
        get_total_time_in_txt(txt_path)
        # print("Done!")
        print("")

def spleet_pth(input_pth):
    output_pth = Config.datahub_root+"musdb18hq/spleeter_out/netease/"
    for each in os.listdir(input_pth):
        print(each)
        # if (os.path.exists(output_pth + each + "/" + "output/combined/vocals.wav")
        #         and os.path.exists(output_pth + each + "/" + "output/combined/accompaniment.wav")):
        #     continue
        os.system("spleeter separate -i " + input_pth + each + " -p spleeter:2stems -o "
                  + output_pth + each)

def unify(source,target):
    source_max = np.max(np.abs(source))
    target_max = np.max(np.abs(target))
    source = source.astype(np.float32)/source_max
    return (source*target_max).astype(np.int16),target

def eval_spleeter():
    from evaluate.sdr import sdr_evaluate
    wh = WaveHandler()
    from evaluate.si_sdr_numpy import sdr,si_sdr
    output_test_pth = Config.datahub_root+"musdb18hq/spleeter_out/test/"
    mus_test_pth= Config.datahub_root+"musdb18hq/test/"

    vocal = []
    background = []
    #
    # for each in os.listdir(mus_train_pth):
    #     mus_dir = mus_train_pth + each + "/"
    #     out_dir = output_train_pth + each + "/output/combined/"
    #     # try:
    #     mus_vocal = wh.read_wave(mus_dir + "vocals.wav")
    #     mus_background = wh.read_wave(mus_dir + "background.wav")
    #     output_vocal = wh.read_wave(out_dir + "vocals.wav")
    #     output_background = wh.read_wave(out_dir + "accompaniment.wav")
    #
    #     output_vocal, mus_vocal = unify(output_vocal, mus_vocal)
    #     output_background, mus_background = unify(output_background, mus_background)
    #
    #     v = sdr(output_vocal, mus_vocal)
    #     b = sdr(output_background, mus_background)
    #     vocal.append(v)
    #     background.append(b)
    #     print("FileName: ",each, "\tSDR-VOCAL: ",v,"SDR-BACKGROUND: " ,b)

    for each in sorted(os.listdir(musdb_test_pth)):
        mus_dir = mus_test_pth+each+"/"
        out_dir = output_test_pth+each+"/output/combined/"
        # try:
        mus_vocal = wh.read_wave(mus_dir+"vocals.wav")
        mus_background = wh.read_wave(mus_dir+"background.wav")
        output_vocal = wh.read_wave(out_dir+"vocals.wav")
        output_background = wh.read_wave(out_dir+"accompaniment.wav")

        output_vocal, mus_vocal = unify(output_vocal,mus_vocal)
        output_background,mus_background = unify(output_background,mus_background)

        v = sdr(output_vocal,mus_vocal)
        b = sdr(output_background,mus_background)
        vocal.append(v)
        background.append(b)
        print("FileName: ",each, "\tSDR-BACKGROUND: " ,b,"\tSDR-VOCAL: ",v)
        # except:
        #     print("Error",each)
    print("AVG-SDR-VOCAL",sum(vocal)/len(vocal))
    print("AVG-SDR-BACKGROUND",sum(background)/len(background))

def filter_data(pth):
    if(pth[-1] != '/'):
        raise ValueError("Error: pth should end with /")
    for each in os.listdir(pth+"hhliu/"):
        if(os.path.exists(pth+each)):
            continue
        print(each)
        data = load_pickle(pth+"hhliu/"+each)
        plt.ylim(-0.2,1)
        plt.plot(data)
        plt.title(each)
        plt.savefig(pth+"pics/"+each.split(".")[-2]+".png")
        break

def bad_data_statistic():
    def split_last_space(raw):
        place = []
        for i in range(0,len(raw)):
            if(raw[i] == " "):
                place.append(i)
        i = place[-1]
        return raw[:i],raw[i+1:]


    data = readList(Config.project_root+"bad_datas.txt")
    dict = {}
    musdb = {}
    kpop = {}
    song = {}
    for i in range(len(data)):
        key = split_last_space(data[i])[0]
        value = float(data[i].strip("\n").split(" ")[-1])
        if(not key in dict.keys()):
            dict[key] = value
        else:
            dict[key] += value
        if('musdb' in key):
            musdb[key] = value
        elif("k_pop" in key):
            kpop[key] = value
        elif("song_data" in key):
            song[key] = value
    print(len(dict.keys()))

    # import matplotlib.pyplot as plt
    # plt.figure(figsize=(12,12))
    # plt.subplot(221)
    # plt.hist(list(dict.values()),bins=400)
    # plt.xlim([-50,450])
    # plt.ylim([0,90])
    # plt.title("All data")
    # plt.xlabel("Certainty of bad data")
    # plt.ylabel("Frequency(times)")
    # plt.subplot(222)
    # plt.hist(list(musdb.values()),bins=20)
    # plt.title("musdb")
    # plt.xlabel("Certainty of bad data")
    # plt.ylabel("Frequency(times)")
    # plt.subplot(223)
    # plt.hist(list(song.values()),bins=20)
    # plt.title("song")
    # plt.xlabel("Certainty of bad data")
    # plt.ylabel("Frequency(times)")
    # plt.subplot(224)
    # plt.hist(list(kpop.values()),bins=20)
    # plt.title("kpop")
    # plt.xlabel("Certainty of bad data")
    # plt.ylabel("Frequency(times)")
    #
    # plt.show()
    write_list(list(dict.keys()),"exclude_list.txt")

def nus_smc_corpus():
    song = Config.datahub_root+"nus-smc-corpus_48/"
    song_dir = []
    for each in os.listdir(song):
        delete_unproper_training_data(song + each+"/sing/")
        for file in os.listdir(song+each+"/sing/"):
            if(file.split('.')[-1] == 'wav'):
                song_dir.append(song + each+"/sing/"+file)
    write_list(song_dir,Config.datahub_root+"datahub/nus_smc_corpus_48.txt")

def activation(x):
    # return 1. / (1 + torch.exp(-100 * (x - 0.1)))
    x[x > 0.1] = 1
    x[x < 0.1] = 0
    return x

def is_restrained(x):
    return abs(x)<1e-2

def is_reserved(x):
    return abs(x-1)<3*1e-2

def posterior_handling(mask, smooth_length=20, freq_bin_portion=0.25):
    mask = mask.squeeze(0)
    freq_bin = mask.shape[0]
    mask_bak = mask.clone()
    mask = mask[:int(freq_bin * freq_bin_portion), :, :]
    mask = torch.sum(torch.sum(mask, 2), 0)
    mask /= torch.max(torch.abs(mask))
    for i in range(mask.shape[0]):
        mask[i] = torch.sum(mask[i - int(smooth_length / 2):i + int(smooth_length / 2)]) / smooth_length
    mask = activation(mask)
    vstart,vend = None,None
    mstart,mend = None,None
    is_vocal = True
    not_music = False
    for i in range(mask.shape[0]):
        if(is_restrained(mask[i]) and is_vocal == True):
            is_vocal = False
            vstart = i
            continue
        elif(not is_restrained(mask[i]) and is_vocal == False):
            is_vocal = True
            vend = i
            if(abs(vend-vstart)<100):
                mask[vstart:vend] = torch.ones(vend-vstart)

    for i in range(mask.shape[0]):
        if(not is_restrained(mask[i]) and not_music == False):
            not_music = True
            mstart = i
            continue
        elif(is_restrained(mask[i]) and not_music == True):
            not_music = False
            mend = i
            if(abs(mend-mstart)<100):
                mask[mstart:mend] = torch.zeros(mend-mstart)

    plt.figure(figsize=(20,5))
    plt.plot(mask.numpy())
    plt.savefig("mask.png")

def merge_model(vocal_model_pth = None,background_model_pth = None):
    model = spleeter.Spleeter(channels=2, unet_inchannels=8, unet_outchannels=8,use_cpu=True)
    vocal_model = torch.load(vocal_model_pth,map_location="cpu")
    background_model = torch.load(background_model_pth,map_location="cpu")
    model.unet1 = vocal_model.unet1
    model.unet0 = background_model.unet0
    model.cnt = 666666
    torch.save(model,"model6660000.pkl")
    print("Done!")

def construct_VCTK(pth = None):
    if(pth == None or pth[-1] != '/'):
        raise ValueError("Error:input pth should end with /")
    dir = []
    for each in os.listdir(pth):
        dir.append(pth+each)
    write_list(dir,"VCTK.txt")

def construct_musdb_splited():
    musdb_train = Config.datahub_root+"musdb18hq_splited/train/"
    train_drum = []
    train_other = []
    train_bass = []
    for each in os.listdir(musdb_train):
        train_drum.append(musdb_train+each+"/drums.wav")
        train_other.append(musdb_train+each+"/other.wav")
        train_bass.append(musdb_train+each+"/bass.wav")
    write_list(train_drum,Config.datahub_root+"datahub/musdb_drum.txt")
    write_list(train_other,Config.datahub_root+"datahub/musdb_other.txt")
    write_list(train_bass,Config.datahub_root+"datahub/musdb_bass.txt")


# merge_model(Config.project_root+"saved_models/1_2020_4_6_DenseUnet_4_4_4_12_0.2_spleeter_sf0_l1_l2_l3_lr0005_bs2-15_fl1.5_ss64000_85lnu5mu0.5sig0.2low0.3hig0.5fshift8flength32drop0split_bandTrue"+"/model368000.pkl",
#             Config.project_root+"saved_models/1_2020_4_6_DenseUnet_4_4_4_12_0.2_spleeter_sf0_l1_l2_l3_lr0005_bs2-15_fl1.5_ss64000_85lnu5mu0.5sig0.2low0.3hig0.5fshift8flength32drop0split_bandTrue"+"/model320000.pkl")

#
# netease_filter(Config.datahub_root+"pure_music_mp3/"
#                ,Config.datahub_root+"pure_music_wav/")
# report_data()
#
# netease_filter("/home/disk2/internship_anytime/liuhaohe/datasets/pure_vocal_mp3/","/home/disk2/internship_anytime/liuhaohe/datasets/pure_vocal_wav/")
# report_data()
# eval_spleeter()


# mask = load_pickle("/home/disk2/internship_anytime/liuhaohe/he_workspace/github/music_separator/util/mask.pkl")
# mask = posterior_handling(torch.Tensor(mask[1]))

# plt.figure(figsize=(20,3))
# plt.imshow(torch.sum(mask,2))
# plt.savefig("temp.png")

# spleet_pth("/home/work_nfs/hhliu/workspace/github/internship_music_separation/evaluate/raw_wave/")