
import json
import os
import thinkdsp as td
import re
import librosa as lb
import soundfile as sf
import shutil



#currently multiplies each file by 12
def make_mods(src_path, save_path, exterior=True, interior=1, tag=None, pitch_up=None, pitch_down=None):


    #os.chdir(src_path)
    for file in os.listdir(src_path):
        if file.endswith('.wav'):
            try:
                y, rate = lb.load(file)
            except:
                print("caught exception")
                continue


        #convert parent audio to parent's sample rate
            if(rate != 44100):
                y = lb.resample(y, rate, 44100)

            if pitch_up is not None:
                pitch_inc(y, file, save_path, tag, pitch_up)

            if pitch_down is not None:
                pitch_dec(y, file, save_path, tag, pitch_down)



        elif file.endswith('.json'):
            if pitch_up is not None:
                pitch_up_json(file, save_path, src_path, pitch_up)
            if pitch_down is not None:
                pitch_down_json(file, save_path, src_path, pitch_down)

        else:
            continue
    #for each new file, create broadcast/normalized versions
    broadcast(save_path, tag)

    rain_src_path = ""#TODO: local directory where background audio and label .json files are stored
    add_rain(save_path, rain_src_path, save_path, tag)


"""*********************************************************  HELPER METHODS  *********************************************************"""

#increases pitch, copies and writes .wav files
def pitch_inc(y, file, save_path, tag, pitch_up):
    for i in range(1, int(pitch_up) + 1):
        data = lb.effects.pitch_shift(y, 44100, n_steps=float(i))
        sf.write(save_path + 'up'+ str(i) +'_' + file, data, 44100, 'PCM_16')
        if tag is not None:
            make_tags(tag, save_path + 'up' + str(i) + '_', file)

def pitch_dec(y, file, save_path, tag, pitch_down):
    for i in range(1,  int(pitch_down + 1)):
        data = lb.effects.pitch_shift(y, 44100, n_steps=float(-1 * i))
        sf.write(save_path + 'down'+ str(i) +'_' + file, data, 44100, 'PCM_16')
        if tag is not None:
            make_tags(tag, save_path + 'down' + str(i) + '_', file)

#for copying .json files to new location
def pitch_up_json(file, save_path, src_path, pitch_up):
    for i in range(1, int(pitch_up) + 1):
        shutil.copyfile(src_path + file, save_path + 'up'+ str(i) + '_' + file)

def pitch_down_json(file, save_path, src_path, pitch_down):
    for i in range(1, int(pitch_down)):
        shutil.copyfile(src_path + file, save_path + 'down'+ str(i) + '_' + file)


def make_tags(tag, save_path, file):
    json_file_name = re.sub("\.wav", ".json", file)
    print(save_path)
    data = {'tags': [tag]}
    with open(save_path+json_file_name, 'w') as outfile:
        json.dump(data, outfile)

def broadcast(src_path, tag):
    #files are sourced and saved from/to the same path
    #normalizes amplitude
    os.chdir(src_path)
    for file in os.listdir(src_path):
        if file.endswith('.wav'):
            wave = td.read_wave(src_path + file)
            carrier_sig = td.CosSignal(freq=10000)
            carrier_wave = carrier_sig.make_wave(duration=wave.duration, framerate=wave.framerate)
            modulated = wave * carrier_wave
            demodulated = modulated * carrier_wave
            demodulated_spectrum = demodulated.make_spectrum(full=True)
            demodulated_spectrum.low_pass(10000)
            filtered = demodulated_spectrum.make_wave()
            filtered.write(filename='BC_' + file)
            #create json file if there is no existing json file provided
            if tag is not None:
                if file.endswith('.wav'):
                    json_file_name = re.sub("\.wav", ".json", file)
                    data = {'tags': [tag]}
                    with open(src_path + 'BC_' + json_file_name, 'w') as outfile:
                        json.dump(data, outfile)
        #copy json file if is provided
        elif tag is None:
            if file.endswith('.json'):
                shutil.copyfile(src_path + file, src_path + 'BC_' + file)

def add_rain(root_src_path, rain_src_path, save_path, tag):
    # read json files in rain directory
    for file in os.listdir(rain_src_path):
        if file.endswith('.json'):
            with open(file) as json_file:
                source_data = json.load(json_file)

                # find background(child) files with rain sounds
                if 'rain' in source_data['tags']:
                    #go to and iterate through root data, create new json files with rain tags and root tags
                    for file_2 in os.listdir(root_src_path):
                        if file_2.endswith('.json'):
                            if tag is not None:
                                os.chdir(save_path)
                                #TODO: Unnecessary?
                                new_json_file = re.sub("\.wav", ".json", file_2)
                                new_json_file = save_path + new_json_file
                                data = {'tags': [tag]}
                                #combine tags from parent and child clips
                                data['tags'].append(source_data['tags'])

                                with open(new_json_file, 'w',) as outfile:
                                    json.dump(data, outfile)
                            #else
                            #TODO: create new json file from two existing json files
                        #add rain sounds to root data
                        elif file_2.endswith('.wav'):
                            os.chdir(root_src_path)
                            child_wave = td.read_wave(filename=file_2)
                            parent_wave = td.read_wave(filename=rain_src_path + file)
                            combine = child_wave + parent_wave
                            combine.normalize()
                            os.chdir(save_path)

                            # format = parent_child.wav
                            product_file_name = re.sub("\.wav", "_", file) + file_2
                            combine.write(product_file_name)







