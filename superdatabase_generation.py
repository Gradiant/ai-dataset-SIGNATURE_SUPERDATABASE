import os
import pandas as pd
import shutil
import json


datasets=['cedar','icdar09','icdar11','bhsig260','utsig','icfhr10','icfhr12']

def get_database_user_id(database_name, user_id, *args):
    out_str =  f"{database_name}_{user_id}"
    for arg in args:
        out_str = f"{out_str}_{arg}"
    return out_str


def parse_cedar(path_to_cedar,dict_org_images, dict_forg_images, database_id_to_global):
    org_path = os.path.join(path_to_cedar,'full_org')
    forg_path = os.path.join(path_to_cedar,'full_forg')
    list_of_org_images = [f for f in os.listdir(org_path) if f.endswith('.png')]
    list_of_forg_images = [f for f in os.listdir(forg_path) if f.endswith('.png')]
    #dict_org_images = {}
    #dict_forg_images = {}
    #database_id_to_global = {}
    global_user_id = len(list(database_id_to_global.values())) - 1
    for org_image in list_of_org_images:
        database_userd_id = get_database_user_id('CEDAR',org_image.split('_')[1])
        if database_userd_id in database_id_to_global.keys():
            global_id = database_id_to_global[database_userd_id]
            dict_org_images[global_id].append(os.path.join(org_path,org_image))
        else:
            global_user_id += 1
            dict_org_images[global_user_id] = [os.path.join(org_path,org_image)]
            database_id_to_global[database_userd_id] = global_user_id

    for forg_image in list_of_forg_images:
        database_userd_id = get_database_user_id('CEDAR',forg_image.split('_')[1])
        if database_userd_id in database_id_to_global.keys():
            global_id = database_id_to_global[database_userd_id]
            if global_id in dict_forg_images.keys():
                dict_forg_images[global_id].append(os.path.join(forg_path,forg_image))
            else:
                dict_forg_images[global_id] = [os.path.join(forg_path,forg_image)]
        else:
            print('SOMETHING WENT WRONG WITH USER '+str(database_userd_id))

def parse_mcyt75(path_mcyt75, dict_org_images, dict_forg_images, database_id_to_global):
    for root, folders, files in os.walk(path_mcyt75):
        img_files = [f for f in files if f.lower().endswith('.bmp')]
        if len(img_files) == 0:
            continue
        global_user_id = len(list(database_id_to_global.values())) - 1
        for img_file in img_files:
            if '_' in img_file:
                #Is a forged signature
                #Name pattern is {attacker_id}_{user_id}f{signature_number}.bmp
                database_user_id = get_database_user_id('MCYT-75',img_file.split('_')[1].split('f')[0])
                if database_user_id in database_id_to_global.keys():
                    global_id = database_id_to_global[database_user_id]
                    dict_forg_images[global_id].append(os.path.join(root,img_file))
                else:
                    global_user_id += 1
                    dict_forg_images[global_user_id] = [os.path.join(root,img_file)]
                    dict_org_images[global_user_id] = []
                    database_id_to_global[database_user_id] = global_user_id
            else:
                # Is a genuine signature
                # Name pattern is {user_id}v{signature_number}.bmp
                database_user_id = get_database_user_id('MCYT-75', img_file.lower().split('v')[0])
                if database_user_id in database_id_to_global.keys():
                    #The user_id already exists: i.e at least one genuine or forged image has been processed
                    global_id = database_id_to_global[database_user_id]
                    dict_org_images[global_id].append(os.path.join(root,img_file))
                else:
                    #User_id does not exist, no signatures from this user have been processed: initilize genuine and
                    #forged sigantures dicts.
                    global_user_id += 1
                    dict_org_images[global_user_id] = [os.path.join(root,img_file)]
                    dict_forg_images[global_user_id] = []
                    database_id_to_global[database_user_id] = global_user_id


def parse_utsig(path_utsig, dict_org_images, dict_forg_images, database_id_to_global):
    for root, folders, files in os.walk(path_utsig):
        img_files = [f for f in files if f.lower().endswith('.tif')]
        if len(img_files) == 0:
            continue
        global_user_id = len(list(database_id_to_global.values())) - 1
        for img_file in img_files:
            if 'Forgery' in root:
                if 'Opposite' in root:
                    #Ignore Opposite hand "attacks"
                    continue
                #Is a forged simg_fileignature
                #User id is in the folder
                database_user_id = get_database_user_id('UTSIG',root.split('/')[-1])
                if database_user_id in database_id_to_global.keys():
                    global_id = database_id_to_global[database_user_id]
                    dict_forg_images[global_id].append(os.path.join(root,img_file))
                else:
                    global_user_id += 1
                    dict_forg_images[global_user_id] = [os.path.join(root,img_file)]
                    dict_org_images[global_user_id] = []
                    database_id_to_global[database_user_id] = global_user_id
            else:
                # Is a genuine signature
                #User id is in the folder
                database_user_id = get_database_user_id('UTSIG', root.split('/')[-1])
                if database_user_id in database_id_to_global.keys():
                    #The user_id already exists: i.e at least one genuine or forged image has been processed
                    global_id = database_id_to_global[database_user_id]
                    dict_org_images[global_id].append(os.path.join(root,img_file))
                else:
                    #User_id does not exist, no signatures from this user have been processed: initilize genuine and
                    #forged sigantures dicts.
                    global_user_id += 1
                    dict_org_images[global_user_id] = [os.path.join(root,img_file)]
                    dict_forg_images[global_user_id] = []
                    database_id_to_global[database_user_id] = global_user_id



def parse_bhsig260(path_bhsig260, dict_org_images, dict_forg_images, database_id_to_global):
    for root, folders, files in os.walk(path_bhsig260):
        img_files = [f for f in files if f.lower().endswith('.tif')]
        if len(img_files) == 0:
            continue
        global_user_id = len(list(database_id_to_global.values())) - 1
        for img_file in img_files:
            if 'F' in img_file:
                #Is a forged simg_fileignature
                #User id is in the folder
                database_user_id = get_database_user_id('BHSIG260',root.split('/')[-1])
                if database_user_id in database_id_to_global.keys():
                    global_id = database_id_to_global[database_user_id]
                    dict_forg_images[global_id].append(os.path.join(root,img_file))
                else:
                    global_user_id += 1
                    dict_forg_images[global_user_id] = [os.path.join(root,img_file)]
                    dict_org_images[global_user_id] = []
                    database_id_to_global[database_user_id] = global_user_id
            elif 'G' in img_file:
                # Is a genuine signature
                #User id is in the folder
                database_user_id = get_database_user_id('BHSIG260', root.split('/')[-1])
                if database_user_id in database_id_to_global.keys():
                    #The user_id already exists: i.e at least one genuine or forged image has been processed
                    global_id = database_id_to_global[database_user_id]
                    dict_org_images[global_id].append(os.path.join(root,img_file))
                else:
                    #User_id does not exist, no signatures from this user have been processed: initilize genuine and
                    #forged sigantures dicts.
                    global_user_id += 1
                    dict_org_images[global_user_id] = [os.path.join(root,img_file)]
                    dict_forg_images[global_user_id] = []
                    database_id_to_global[database_user_id] = global_user_id


def get_icdar09_train_metadata(img_file):
    prefix, user_id, signature_id, suffix = img_file.split('_')
    writer_id = prefix.split('-')[1]
    return writer_id, user_id

def get_icdar09_test_metadata(img_file):
    prefix, suffix = img_file.split('-')
    writer_id = suffix[:3]
    signature_id = suffix[3:5]
    user_id = suffix[5:].split('.')[0]
    return writer_id, user_id

def get_icdar11_train_metadata(img_file):
    preffix, suffix = img_file.split('_')
    if len(preffix) > 3:
        #Is a forgery containing writer_id and user_id
        writer_id = preffix[:4]
        user_id = preffix[4:]
    else:
        #Is a genuine signature containing user_id (writer_id is the same)
        user_id = preffix
        writer_id = user_id
    return writer_id, user_id

def get_icdar11_test_metadata(img_file):
    preffix, suffix = img_file.split('_')
    metadata, ext = suffix.split('.')
    if len(metadata) > 3:
        # Is a forgery containing writer_id and user_id
        writer_id = metadata[:4]
        user_id = metadata[4:]
    else:
        #Is a genuine signature containing user_id (writer_id is the same)
        user_id = metadata
        writer_id = user_id
    if not user_id:
        print('user ID error')
    return writer_id, user_id


def update_dicts_icdar09(img_file, root_path, global_user_id, dict_org_images, dict_forg_images, database_id_to_global, split):
    if split == 'train':
        get_metadata_function = get_icdar09_train_metadata
    else:
        get_metadata_function = get_icdar09_test_metadata
    writer_id, user_id = get_metadata_function(img_file)
    if writer_id != user_id:
        # Is a forged signature
        database_user_id = get_database_user_id(f"ICDAR09_{split}", user_id)
        if database_user_id in database_id_to_global.keys():
            global_id = database_id_to_global[database_user_id]
            dict_forg_images[global_id].append(os.path.join(root_path, img_file))
        else:
            global_user_id += 1
            dict_forg_images[global_user_id] = [os.path.join(root_path, img_file)]
            dict_org_images[global_user_id] = []
            database_id_to_global[database_user_id] = global_user_id
    else:
        # Is a genuine signature
        # User id is in the folder
        database_user_id = get_database_user_id(f"ICDAR09_{split}", user_id)
        if database_user_id in database_id_to_global.keys():
            # The user_id already exists: i.e at least one genuine or forged image has been processed
            global_id = database_id_to_global[database_user_id]
            dict_org_images[global_id].append(os.path.join(root_path, img_file))
        else:
            # User_id does not exist, no signatures from this user have been processed: initilize genuine and
            # forged sigantures dicts.
            global_user_id += 1
            dict_org_images[global_user_id] = [os.path.join(root_path, img_file)]
            dict_forg_images[global_user_id] = []
            database_id_to_global[database_user_id] = global_user_id
    return global_user_id



def parse_icdar09(path_icdar09, dict_org_images, dict_forg_images, database_id_to_global):
    train_path = os.path.join(path_icdar09,'training')
    test_path = os.path.join(path_icdar09,'test')
    #train
    img_files = [f for f in os.listdir(train_path) if f.lower().endswith('.png')]
    global_user_id = len(list(database_id_to_global.values())) - 1
    for img_file in img_files:
        global_user_id = update_dicts_icdar09(img_file,train_path,global_user_id,dict_org_images, dict_forg_images, database_id_to_global,
                             'train')
    #test
    for type_of_signature in ['genuines','forgeries']:
        type_path = os.path.join(test_path,type_of_signature)
        img_files = [f for f in os.listdir(type_path) if f.lower().endswith('.png')]
        global_user_id = len(list(database_id_to_global.values())) - 1
        for img_file in img_files:
            global_user_id = update_dicts_icdar09(img_file, type_path, global_user_id, dict_org_images, dict_forg_images,
                                 database_id_to_global,
                                 'test')

def parse_icdar11(path_icdar09, dict_org_images, dict_forg_images, database_id_to_global):
    for root, folders, files in os.walk(path_icdar09):
        img_files = [f for f in files if f.lower().endswith('.png')]
        if len(img_files) == 0:
            continue
        global_user_id = len(list(database_id_to_global.values())) - 1
        for img_file in img_files:
            if 'training' in root:
                is_training = True
                writer_id, user_id = get_icdar11_train_metadata(img_file)
            else:
                is_training = False
                writer_id, user_id = get_icdar11_test_metadata(img_file)
            if 'Chinese' in root:
                origin = 'Chinese'
            else:
                origin = 'Dutch'
            if writer_id != user_id:
                # Is a forged signature
                # User id is in the folder
                if is_training:
                    database_user_id = get_database_user_id('ICDAR11_train', user_id,origin)
                else:
                    database_user_id = get_database_user_id('ICDAR11_test', user_id,origin)
                if database_user_id in database_id_to_global.keys():
                    global_id = database_id_to_global[database_user_id]
                    dict_forg_images[global_id].append(os.path.join(root, img_file))
                else:
                    global_user_id += 1
                    dict_forg_images[global_user_id] = [os.path.join(root, img_file)]
                    dict_org_images[global_user_id] = []
                    database_id_to_global[database_user_id] = global_user_id
            else:
                # Is a genuine signature
                # User id is in the folder
                if is_training:
                    database_user_id = get_database_user_id('ICDAR11_train', user_id, origin)
                else:
                    database_user_id = get_database_user_id('ICDAR11_test', user_id, origin)
                if database_user_id in database_id_to_global.keys():
                    # The user_id already exists: i.e at least one genuine or forged image has been processed
                    global_id = database_id_to_global[database_user_id]
                    dict_org_images[global_id].append(os.path.join(root, img_file))
                else:
                    # User_id does not exist, no signatures from this user have been processed: initilize genuine and
                    # forged sigantures dicts.
                    global_user_id += 1
                    dict_org_images[global_user_id] = [os.path.join(root, img_file)]
                    dict_forg_images[global_user_id] = []
                    database_id_to_global[database_user_id] = global_user_id


def parse_icfhr10(path_icfhr10, dict_org_images, dict_forg_images, database_id_to_global):
    for root, folders, files in os.walk(path_icfhr10):
        img_files = [f for f in files if f.lower().endswith('.png')]
        if len(img_files) == 0:
            continue
        global_user_id = len(list(database_id_to_global.values())) - 1
        for img_file in img_files:
            if 'Training' in root:
                is_training = True
               # writer_id, user_id = get_icdar11_train_metadata(img_file)
            else:
                is_training = False
                #writer_id, user_id = get_icdar11_test_metadata(img_file)
            if is_training:
                # Only one user in training and another in testing
                database_user_id = 'ICFHR10_01'
                if 'Genuine' in root or 'Reference' in root:
                    if database_user_id in database_id_to_global.keys():
                        # The user_id already exists: i.e at least one genuine or forged image has been processed
                        global_id = database_id_to_global[database_user_id]
                        dict_org_images[global_id].append(os.path.join(root, img_file))
                    else:
                        # User_id does not exist, no signatures from this user have been processed: initilize genuine and
                        # forged sigantures dicts.
                        global_user_id += 1
                        dict_org_images[global_user_id] = [os.path.join(root, img_file)]
                        dict_forg_images[global_user_id] = []
                        database_id_to_global[database_user_id] = global_user_id
                elif 'Simulated' in root:
                    if database_user_id in database_id_to_global.keys():
                        global_id = database_id_to_global[database_user_id]
                        dict_forg_images[global_id].append(os.path.join(root, img_file))
                    else:
                        global_user_id += 1
                        dict_forg_images[global_user_id] = [os.path.join(root, img_file)]
                        dict_org_images[global_user_id] = []
                        database_id_to_global[database_user_id] = global_user_id
            else:
                database_user_id = 'ICFHR10_02'
                if 'Reference' in root:
                    if database_user_id in database_id_to_global.keys():
                        # The user_id already exists: i.e at least one genuine or forged image has been processed
                        global_id = database_id_to_global[database_user_id]
                        dict_org_images[global_id].append(os.path.join(root, img_file))
                    else:
                        # User_id does not exist, no signatures from this user have been processed: initilize genuine and
                        # forged sigantures dicts.
                        global_user_id += 1
                        dict_org_images[global_user_id] = [os.path.join(root, img_file)]
                        dict_forg_images[global_user_id] = []
                        database_id_to_global[database_user_id] = global_user_id
                elif 'Questioned' in root:
                    signature_id = int(img_file[1:4])
                    if signature_id in [49,52,66]:
                        #Genuine
                        if database_user_id in database_id_to_global.keys():
                            global_id = database_id_to_global[database_user_id]
                            dict_org_images[global_id].append(os.path.join(root, img_file))
                        else:
                            global_user_id += 1
                            dict_forg_images[global_user_id] = [os.path.join(root, img_file)]
                            dict_org_images[global_user_id] = []
                            database_id_to_global[database_user_id] = global_user_id
                    elif signature_id in [6,15,28,29,34,87,90]:
                        #Disguised signature, ignore
                        continue
                    else:
                        #Forgery
                        if database_user_id in database_id_to_global.keys():
                            global_id = database_id_to_global[database_user_id]
                            dict_forg_images[global_id].append(os.path.join(root, img_file))
                        else:
                            global_user_id += 1
                            dict_forg_images[global_user_id] = [os.path.join(root, img_file)]
                            dict_org_images[global_user_id] = []
                            database_id_to_global[database_user_id] = global_user_id


def parse_icfhr12(path_icfhr12, dict_org_images, dict_forg_images, database_id_to_global):
    xls = pd.ExcelFile(os.path.join(path_icfhr12,'Correct_Anwsers_Key.xls'))
    dict_gt = {}
    dict_gt['A1'] = pd.read_excel(xls, 'A1').to_numpy().astype('int')
    dict_gt['A2'] = pd.read_excel(xls, 'A2').to_numpy().astype('int')
    dict_gt['A3'] = pd.read_excel(xls, 'A3').to_numpy().astype('int')
    for root, folders, files in os.walk(path_icfhr12):
        img_files = [f for f in files if f.lower().endswith('.png')]
        if len(img_files) == 0:
            continue
        global_user_id = len(list(database_id_to_global.values())) - 1
        for img_file in img_files:
            # Only one user in training and another in testing
            user_id = 'A1'
            if 'A2' in root:
                user_id = 'A2'
            if 'A3' in root:
                user_id = 'A3'
            database_user_id = f"ICFHR12_{user_id}"
            if 'Ref' in root:
                if database_user_id in database_id_to_global.keys():
                    # The user_id already exists: i.e at least one genuine or forged image has been processed
                    global_id = database_id_to_global[database_user_id]
                    dict_org_images[global_id].append(os.path.join(root, img_file))
                else:
                    # User_id does not exist, no signatures from this user have been processed: initilize genuine and
                    # forged sigantures dicts.
                    global_user_id += 1
                    dict_org_images[global_user_id] = [os.path.join(root, img_file)]
                    dict_forg_images[global_user_id] = []
                    database_id_to_global[database_user_id] = global_user_id
            elif 'Questioned' in root:
                signature_id = int(img_file[1:4])
                if signature_id in dict_gt[user_id][:,2]:
                    if database_user_id in database_id_to_global.keys():
                        global_id = database_id_to_global[database_user_id]
                        dict_forg_images[global_id].append(os.path.join(root, img_file))
                    else:
                        global_user_id += 1
                        dict_forg_images[global_user_id] = [os.path.join(root, img_file)]
                        dict_org_images[global_user_id] = []
                        database_id_to_global[database_user_id] = global_user_id
                elif signature_id in dict_gt[user_id][:,1]:
                    if database_user_id in database_id_to_global.keys():
                        # The user_id already exists: i.e at least one genuine or forged image has been processed
                        global_id = database_id_to_global[database_user_id]
                        dict_org_images[global_id].append(os.path.join(root, img_file))
                    else:
                        # User_id does not exist, no signatures from this user have been processed: initilize genuine and
                        # forged signatures dicts.
                        global_user_id += 1
                        dict_org_images[global_user_id] = [os.path.join(root, img_file)]
                        dict_forg_images[global_user_id] = []
                        database_id_to_global[database_user_id] = global_user_id

def generate_superdatabase(dict_org_images, dict_forg_images, database_id_to_global, path_to_superdatabase):
    os.makedirs(path_to_superdatabase,exist_ok=True)
    dict_signature_correspondences = {}
    for database_id, list_signatures in dict_org_images.items():
        signature_cont = 0
        for signature in list_signatures:
            _, ext = os.path.splitext(signature)
            database_filename = "{0:04d}_g_{1:03d}".format(database_id,signature_cont)+ext
            signature_cont += 1
            output_path = os.path.join(path_to_superdatabase,database_filename)
            shutil.copyfile(signature,output_path)
            split_signature = signature.split('/')
            start_index = split_signature.index('firmas')
            relative_path = '/'.join(split_signature[start_index+1:])
            dict_signature_correspondences[database_filename] = relative_path
    for database_id, list_signatures in dict_forg_images.items():
        signature_cont = 0
        for signature in list_signatures:
            _, ext = os.path.splitext(signature)
            database_filename = "{0:04d}_f_{1:03d}".format(database_id,signature_cont)+ext
            signature_cont += 1
            output_path = os.path.join(path_to_superdatabase, database_filename)
            shutil.copyfile(signature, output_path)
            split_signature = signature.split('/')
            start_index = split_signature.index('firmas')
            relative_path = '/'.join(split_signature[start_index + 1:])
            dict_signature_correspondences[database_filename] = relative_path

    with open(os.path.join(path_to_superdatabase,'ids.json'), 'w') as fp:
        json.dump(database_id_to_global, fp)
    with open(os.path.join(path_to_superdatabase,'signatures.json'), 'w') as fp:
        json.dump(dict_signature_correspondences, fp)



if __name__ == '__main__':
    dict_org_images = {}
    dict_forg_images = {}
    database_id_to_global = {}
    parse_cedar('/home/jjmoreira/Documentos/firmas/CEDAR/signatures',dict_org_images,dict_forg_images,database_id_to_global)
    parse_mcyt75('/home/jjmoreira/Documentos/firmas/MCYT75',dict_org_images,dict_forg_images,database_id_to_global)
    parse_utsig('/home/jjmoreira/Documentos/firmas/UTSig',dict_org_images,dict_forg_images,database_id_to_global)
    parse_bhsig260('/home/jjmoreira/Documentos/firmas/BHSig260',dict_org_images,dict_forg_images,database_id_to_global)
    parse_icdar09('/home/jjmoreira/Documentos/firmas/icdar2009',dict_org_images,dict_forg_images,database_id_to_global)
    parse_icdar11('/home/jjmoreira/Documentos/firmas/icdar2011',dict_org_images,dict_forg_images,database_id_to_global)
    parse_icfhr10('/home/jjmoreira/Documentos/firmas/Dataset_4NSigComp2010',dict_org_images,dict_forg_images,database_id_to_global)
    parse_icfhr12('/home/jjmoreira/Documentos/firmas/4nSigComp2012/Testset_4NsigComp2012',dict_org_images,dict_forg_images,database_id_to_global)
    generate_superdatabase(dict_org_images,dict_forg_images,database_id_to_global,'/home/jjmoreira/Documentos/superdatabase')
    print(dict_org_images)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
