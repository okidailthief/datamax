
import synthesize as syn



src_path = '' #TODO: path to local directory where source dataset/label files can be found
save_path = ''#TODO: path to local directory to which new data should be written
tag = None #TODO: insert tag for source audio here
#if source files for duplication have associated json files with tags, leave tag field blank
syn.make_mods(src_path, save_path, exterior=True, tag='cat', pitch_up=3.0, pitch_down=3.0)

