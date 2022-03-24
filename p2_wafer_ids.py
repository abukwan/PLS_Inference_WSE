from nltk.tokenize import WhitespaceTokenizer
import numpy as np
import shutil


def preprocess(text: str):
    # ---------------- Preprocessing : add white space in order to keep/exclude char. -----
    # char. lower
    text = text.lower()
    # separate symbol
    # Brackets condition
    check_char_list = ["(#", "(wafer", "(w"]
    for check_char in check_char_list:
        if check_char in text:
            text = text.replace('(', ' ( ')
            text = text.replace(')', ' ) ')
    # separate special symbol
    text = text.replace(',', ' , ')
    text = text.replace('-', ' - ')
    text = text.replace('~', ' ~ ')
    text = text.replace('/', ' / ')
    text = text.replace('[', ' [ ')
    text = text.replace(']', ' ] ')
    text = text.replace('@', ' @ ')
    text = text.replace(':', ' : ')
    text = text.replace('#', ' # ')
    # separate special words for excluding invalid string
    text = text.replace('bin', 'bin ')
    text = text.replace('sbin', 'sbin ')
    text = text.replace('hbin', 'hbin ')
    text = text.replace('hb', 'hb ')
    text = text.replace('sb', 'sb ')
    text = text.replace('wafer', 'wafer ')

    # each wafer id separate some consist
    for i in range(25, 0, -1):
        #print(i)
        # continual with wafer id + other char.
        # don't separate "." + num , cuz lot id contains "xxxxxxxx.1"
        continual_wafer = str(i) + "."
        continual_wafer_f = str(i) + " ."
        text = text.replace(continual_wafer, continual_wafer_f)
        continual_wafer = str(i) + "("
        continual_wafer_f = str(i) + " ("
        text = text.replace(continual_wafer, continual_wafer_f)
        continual_wafer = str(i) + ";"
        continual_wafer_f = str(i) + " ;"
        text = text.replace(continual_wafer, continual_wafer_f)
        continual_wafer = "w" + str(i)
        continual_wafer_f = " w " + str(i)
        text = text.replace(continual_wafer, continual_wafer_f)
    #print(text)
    return text


def fill_wafer_id(text: str):
    # structure: fill all wafer id between start chars and end chars.
    # ----------- find words type loc and fix not valid word to '0' --------------------------------
    # Only keep special char.
    special_char = ['#', '-', '~', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
                    '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24',
                    '25', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'bin', 'wafer', 'sbin', 'hbin',
                    'hb', 'sb', 'wafers', 'w']
    word_list = WhitespaceTokenizer().tokenize(preprocess(text))
    final_words = []
    for word in word_list:
        if word in special_char:
            final_words.append(word)
    arr = final_words
    #print("Before:")
    #print(arr)
    # Define char.
    id_char = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15',
               '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '1', '2', '3', '4', '5', '6',
               '7', '8', '9']
    serial_char = ['-', '~']
    start_char = ['#', 'wafer', 'wafers', 'w']
    end_char = ['bin', 'sb', 'hbin', 'sbin', 'hb']
    # wafer id starting symbol index
    start_index = [i for i, x in enumerate(arr) if x in start_char]
    start_index.sort()
    # till end
    start_index.append(len(arr))
    # start with
    start_min_index = np.min(start_index)
    arr = arr[start_min_index:]
    # end symbol index
    end_index = [i for i, x in enumerate(arr) if x in end_char]
    end_index.sort()
    # pair: if need fix range to array[[$start1,$end1],[$start2,$end2]...]
    need_fix_dis = []
    if len(end_index) > 0:
        for end in end_index:
            tmp_start_index = [a for a in start_index if a > end]
            if len(tmp_start_index) > 0:
                need_fix_dis.append([end, min(tmp_start_index)])
        for need_fix in need_fix_dis:
            fix_low = need_fix[0]
            fix_high = need_fix[1]
            # fix '0' during issue-char. range
            arr[fix_low: fix_high] = ['0'] * (fix_high - fix_low)
    # all listed wafer id
    arr_id = [a for a in arr if a in id_char]
    wafer_id_result = []
    if len(arr_id) > 0:
        # wafer id index
        arr_id_index = [i for i, x in enumerate(arr) if x in id_char]
        # max wafer id index
        max_id_index = np.max(arr_id_index)
        # serial symbol index
        serial_index = [i for i, x in enumerate(arr) if x in serial_char]
        serial_index_fix = [a for a in serial_index if a < max_id_index]
        # valid serial symbol index (including previous and next)
        serial_index_f = [a for a in serial_index_fix if a - 1 in arr_id_index and a + 1 in arr_id_index]
        # fill wafer id between start and end
        for n in serial_index_f:
            start_wafer = int(arr[n - 1])
            end_wafer = int(arr[n + 1])
            dis_qty = end_wafer - start_wafer
            for j in range(start_wafer + 1, start_wafer + dis_qty):
                wafer_id_result.append(j)
        for n in arr_id:
            wafer_id_result.append(int(n))
    else:
        # if there is no wafer id
        wafer_id_result.append(0)
    # distinct wafer id
    unique_wafer_ids = list(set(wafer_id_result))
    unique_wafer_ids.sort()
    wafer_qty = len([e for e in unique_wafer_ids if e > 0])
    return [unique_wafer_ids, wafer_qty]


def split_action(text: str):
    # structure: fail contribute chars ←→ [wafer_id] ←→ pass contribute chars ←→ [wafer_id]
    # ---- to find pass/fail loc to define sub string and call fill wafer id to process it.---
    #wafer_start_chars = ['#', 'wafer', 'wafers', 'w']
    wafer_start_chars = ['#', 'wafer', 'wafers', 'w']
    fail_chars = ['hold', 'rma', '2nd_sbc_rwk', 'retest', 'to_ems', 'scrap', 'reporbe',
                  'get', 'sort', 'rt', 'put', 'fail_hold']
    pass_chars = ['release', 'flow', 'pass_go', 'split', 'pgfh']
    id_substitution = ['other', 'others', 'remain', 'remains', 'reject', 'rejects', 'good', 'goods']
    text = preprocess(text)
    # group specific chars consists by "_"
    text = text.replace('pass go', 'pass_go')
    text = text.replace('2nd sbc rwk', '2nd_sbc_rwk')
    text = text.replace('to ems', 'to_ems')
    text = text.replace('fail hold', 'fail_hold')
    #print(text)

    word_list = WhitespaceTokenizer().tokenize(preprocess(text))
    #print(word_list)
    # add pass action
    action_loc = []
    pass_loc = [i for i, x in enumerate(word_list) if x in pass_chars]
    action_loc.extend(pass_loc)
    # add fail action
    fail_loc = [i for i, x in enumerate(word_list) if x in fail_chars]
    action_loc.extend(fail_loc)
    action_loc.sort()
    # wafer id start loc
    wafer_start_loc = [i for i, x in enumerate(word_list) if x in wafer_start_chars]

    # to get wafer id
    # --- action sorting direction ←  -----
    sub_end = len(word_list)
    sub_string = ""
    action_seq = len(action_loc) - 1
    split_wafer_ids = []
    #   --to consist action related sub string
    if action_seq >= 0:
        for i in range(len(wafer_start_loc)-1, -1, -1):
            # consist sub string
            for j in range(wafer_start_loc[i], sub_end, 1):
                sub_string = sub_string + " " + str(word_list[j])
            # after consist sub string , fill all wafer id of sub string
            sub_wafer_ids = fill_wafer_id(sub_string)
            #   --- if wafer qty = 0, check if there are wafer id substitution words in the action
            if sub_wafer_ids[1] == 0:
                #after_action_string = ""
                substitution = False
                for k in range(action_loc[action_seq], sub_end, 1):
                    if word_list[k] in id_substitution:
                        substitution = True
                #if find wafer id substitution set wafer qty to 999
                if substitution is True:
                    sub_wafer_ids[1] = 999
                    substitution = False
            # assign next sub end loc
            sub_end = wafer_start_loc[i] - 1

            # if wafer qty > 0 , find related action
            if sub_wafer_ids[1] > 0:
                action_index = action_loc[action_seq]
                action_char = word_list[action_index]
                if action_char in pass_chars:
                    action_type = "P"
                else:
                    action_type = "F"
                sub_wafer_ids.extend(action_type)
                #print(sub_wafer_ids)
                split_wafer_ids.append(sub_wafer_ids)
                action_seq -= 1
            sub_string = ""
    #print(split_wafer_ids)
    return split_wafer_ids


if __name__ == "__main__":
    # for test
    #txt = " 根據ILM指示, 請協助以下貨批處置, THANKS. " \
    #       " 1.	Split wafer #01-07, #09-14, #16-25 為子批63M7N993.2" \
    #       " 2.	Release  子批63M7N993.2 " \
    #       " 3.	母批 63M7N993.1  (wafer #08, #15) 繼續Hold住"

    txt = "Hold w#7,8,10~12 and release w#9."
    #txt = "Hold W#17 and release other wafer ,thanks"
    #txt = "Hold w#2,4,5,8,10,12,15,17,18,20~22,24 and release w#1,3,6,7,9,11,13,14,16,19,23,25."

    #txt = "Please release wf#08 to next process, I future hold to VM and wait inoff dice."
    a = split_action(txt)
    print(a)
    #txt1 = "# 08 ~ 11"
    #print(fill_wafer_id(txt1))

    # copy files to other app
    file1 = '/home/paulliao/APP/AI_NLP_classification/Inference/API/p2_wafer_ids.py'
    dst1 = '/home/paulliao/APP/AI_NLP_classification/Inference/p2_wafer_ids.py'
    dst2 = '/home/paulliao/APP/AI_NLP_classification/WSE/p2_wafer_ids.py'
    shutil.copyfile(file1, dst1)
    shutil.copyfile(file1, dst2)
    print("copy done.")
