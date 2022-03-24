from nltk.tokenize import WhitespaceTokenizer
import numpy as np
import shutil


def fill_wafer_id(text: str):
    # ---------------- Preprocessing : add white space in order to  keep/exclude char.
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

    #print(text)
    # each wafer id separate some consist
    for i in range(25, 0, -1):
        # end with "."  ()
        #end_wafer = str(i) + "."
        #end_wafer_f = str(i) + " ."
        #if text.endswith(end_wafer):
        #    text = text.replace(end_wafer, end_wafer_f)

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
    # -----------find words type loc and fix not valid word to '0' ----------------------
    # Only keep special char.
    special_char = ['#', '-', '~', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
                    '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24',
                    '25', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'bin', 'wafer', 'sbin', 'hbin',
                    'hb', 'sb', 'wafers', 'w']
    word_list = WhitespaceTokenizer().tokenize(text)
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
    # cal. if need fix range to array[[$start1,$end1],[$start2,$end2]...]
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
        for n in serial_index_f:
            start_wafer = int(arr[n - 1])
            end_wafer = int(arr[n + 1])
            dis_qty = end_wafer - start_wafer
            for j in range(start_wafer + 1, start_wafer + dis_qty):
                wafer_id_result.append(j)
        for n in arr_id:
            wafer_id_result.append(int(n))
    else:
        wafer_id_result.append(0)
    unique_wafer_ids = list(set(wafer_id_result))
    unique_wafer_ids.sort()
    wafer_qty = len([e for e in unique_wafer_ids if e > 0])
    return [unique_wafer_ids, wafer_qty]


if __name__ == "__main__":

    #txt = " Pls hold wafer#03,07 and release wafer#08"
    txt = "Please shift site to retest W#2~8.15.16.19.22~24 Bin 2-5,7,8"
    print(fill_wafer_id(txt))
    file1 = '/home/paulliao/APP/AI_NLP_classification/Inference/API/wafer_ids.py'
    dst1 = '/home/paulliao/APP/AI_NLP_classification/Inference/wafer_ids.py'
    dst2 = '/home/paulliao/APP/AI_NLP_classification/WSE/wafer_ids.py'
    shutil.copyfile(file1, dst1)
    shutil.copyfile(file1, dst2)
    print("copy done.")

