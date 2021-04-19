import g



# Helper functions

def most_freq_element(aList):
    from collections import Counter
    freqc = Counter(aList)
    return freqc.most_common(1)[0][0]

def match_on_initial(word1,word2):
    if len(word1) < 2 or len(word2) < 2:
        return False
    elif (word1[0] == word2[0]) and (word1[1] == '.' or word2[1] == '.'):
        return True
    else:
        return False


def general_match(word1, word2):
    if word1.lower() == word2.lower():
        return True
    elif len(word1) > 2 and len(word1) == len(word2) + 2:
        if word1[0] == '(' and word1[len(word1) - 1] == ')' and word1[1:len(word1) - 1].lower() == word2.lower():
            return True
    elif len(word2) > 2 and len(word2) == len(word1) + 2:
        if word2[0] == '(' and word2[len(word2) - 1] == ')' and word2[1:len(word2) - 1].lower() == word1.lower():
            return True
    else:
        return False


def removejunk(astring):
    junkchars = {'@', '^', '%'}

    if astring == '':
        return ''
    else:
        njunk = 0
        alist = []
        for char in astring:
            if char in junkchars:

                print(astring)
            else:
                alist.append(char)
        return ''.join(alist)

def addspaceafterperiod(astring):
    if astring == '':
        return ''
    else:
        alist = []
        for i, char in enumerate(astring):
            if i < len(astring) - 1:
                if char == '.' and astring[i+1] != ' ':
                    alist.append('. ')
                else:
                    alist.append(char)
        alist.append(astring[len(astring)-1])
        return ''.join(alist)

#print(addspaceafterperiod(''))


class fs_corrupted(g.PropertyCoder):
    def run(self):
        # corrupted doesnt mean there is necessarily no information, but that there are also confusing elements
        n_fs_corrupt = 0

        # these are problem duplicated names found by inspection at various points
        duplicatedtextinFS = {14816, 21826, 25212, 25214, 57251, 59654, 59809, 15744, 37771, 44247, 59809}

        # these are ok although loot corrupted
        fsOK = {28520}

        fsn_split = self["firstSentence"].split(' ')
        if fsn_split[0] == "By" and fsn_split[1][0].isupper():
            return True
        if fsn_split[0] == '.' or fsn_split[0] == ',':
            return True
        if self['id'] in duplicatedtextinFS:
            return True
        if self['id'] in fsOK:
            return False

        return False

class title_corrupted(g.PropertyCoder):
    def run(self):
        # find titles that are corrupted and thus title does not provide a good clue to obit name
        title_corrupted_individually_seen = {19161, 37480, 38228}
        titles_OK_individually_seen = {31977, 38298, 469, 59944, 25264, 60563}

        # check if all letters in titles are caps, this is often sign of a title that
        # simply gives obituarizeds name
        # in check elsewhere, only titles < 8 chars that were names were all in caps
        # used especially in 1980
        # but see 17499 17239 for titles that are all caps but phrases that dont include obit name

        tsna_split = self["title"].split(' ')
        tsn_all_letters_caps = True
        for w in tsna_split:
            if not w.isupper():
                tsn_all_letters_caps = False

        if self["id"] in title_corrupted_individually_seen:
            return True
        # Final Edition and Late Edition this covers all "edition" in title where not a legitimate obituary
        if "Final Edition" in self["title"] or "Late Edition" in self["title"]:
            return True
        #    print(self["id"],self["title"])
        if len(self["title"]) < 12 and not tsn_all_letters_caps:
            return True
        if self["id"] in titles_OK_individually_seen:
            return False

class not_obit(g.PropertyCoder):
    # not obits
    not_obits = {501, 7166, 10608, 10897, 12175, 14228, 19352, 19595, 20990, 22001, 20035, 23625, 23373, 23399, 23451,
                 23480, 23399, 23634,
                 23851, 24633, 26957, 33575, 36687, 36531, 36802, 37335, 38277, 38317, 41070, 42682, 44206, 44400,
                 44568, 47831, 51563, 52101, 52109, 52252,
                 57459, 58018,
                 11383, 13269, 17320, 19181, 21310, 21846, 22184, 23466, 25887, 28268, 28439, 32537, 32585, 39133,
                 39293, 42786, 47906, 48008,
                 50878, 52985, 59648, 59682, 59685, 60679, 874, 9631,
                 26205, 28775, 33016, 56538, 5930,
                 584, 59593, 60402, 21141, 24333, 15364, 16482, 444495, 11760, 12064, 12786, 13222, 14115, 1725, 21599,
                 39133, 50320,
                 23581, 25356, 19943, 14518, 44495, 4389, 46000, 48095.48202, 54220, 8084, 3942, 38413, 13364, 23488,
                 52147, 566, 57594, 18897,
                 33373, 35777, 56892, 59789, 60705, 11218, 15896, 18536, 34790, 18659, 40202}

    # these describe someone apparently after their death but may be commentary rather than regular obit
    # doesnt contain usual sentences about death, survivors
    # 2468 is liz taylor 33575 is tom petty
    # not excluding these
    bio_of_deadorundead = {2468, 33575, 3555, 25909}

    # deaths of 2 or more people (as in couple killed in auto accident)
    multipledeaths = {42842, 39738, 17036, 32760, 19145, 56658}

    # deaths of unknowns, death rather than the life is central
    accidents = {43681, 44112, 44001}

    # these found by searching for memorial in title, some above are also memorials were excluded from search
    memorials = {14190, 32092, 35731, 35764, 36397, 37447, 39421, 43372.4362, 46152, 50941, 51350, 51402, 53570, 59068,
                 6859, 21141,
                 23776, 23592, 4362, 44491, 56890, 48804, 52047, 53976, 16702, 18818, 55630, 10608}

    # accounts of someone recently dead (like 23282, cancer patient that are not standard obits
    # not currently excluding
    nonstd_obitlike = {23282, 29675, 14418}
    # print("Not obits")

    # articles that look like they are not obits but are
    legit_1wordLastname = {36326, 31331}

    def run(self):
        return self['id'] in self.not_obits or self["id"] in self.multipledeaths or self["id"] in self.memorials or self["id"] in self.accidents














# ----------------------------------


class name_prior(g.PropertyCoder):
    def run(self):
        # pure split comma literal AND pure comma literal

        # does not use Stanford Person; if text before comma in title and fs match then its a match
        # if not a simple equivalence, then tests in various ways for whether fs comma-delimited segment contains the words appearing in title comma-delimited segment

        # this allows a match if the fs name has more detail on middle names, as it often does
        # but is dangerous, since short title segments (including artificially short stubs like "D") may match lots of things
        # also difficult to know which segment to keep as the name, longer fs segments may contain non-name material (Bill Smith of Ithaca)
        # while title segments lack detail on middle names and may be stubs

        # lots of titles start with all caps, so name-like phrase is not a strong test for title, its a better test for fs

        # best match is pure comma literal (match, name) exactly equal
        # next is more_expansive, matches on 2 or more words, cuts out extraneous
        # next is t contains f or f contains t, also extraneous are cut out

        import re

        # this is where we'll store the results
        ret = {}

        # note its ' is dead' not 'is dead'
        pats = [',', ';', ':', ' --', ' is dead', ' dies', ' dead', ' died']

        # do not extract NobelTitles because these often form part of the most used name
        NobleTitles = ['Lord', 'Lady', 'Earl', 'Count', 'Viscount', 'Sultan', 'Baroness', 'Baron']

        ReligiousTitles = ['Grand Rabbi', 'Rabbi', 'Elder', 'His Beatitude', 'The Right', 'The Very', 'The Most',
                           'The Venerable',
                           'The Rev.', 'The Reverend', 'Rev.', 'Reverend', 'Father', 'Cardinal', 'Msgr.',
                           'Monsignor', 'Auxiliary', 'Bishop', 'Archbishop']
        # dont extract Marhal because Marshall is a name
        ProfessionalTitles = ['Doctor', 'Dr.', 'Professor', 'Prof', 'Prof.']
        MilitaryTitles = ['RearWorld War II Rear Adm.', 'Grand Adm.', 'RearWorld War II Adm.', 'Capt.',
                          'Group Captain', 'Wing Comdr.', 'Liet Gen.', 'Navy Comdr.', 'Field Marshal',
                          'Grand Marshal', 'Air Vice Marshal', 'Vice Adm.', 'Rear Adm.', 'Vice Admiral',
                          'Rear Admiral', 'Admiral', 'Adm.', 'Air Marshal', 'Commodore', 'Sgt.', 'Warrant Officer',
                          'Lt.', 'Lieut.', 'Maj.', 'Major', 'Col.', 'Colonel', 'Brig.', 'Brigadier', 'General',
                          'Gen.', 'Captain', 'Capt.', 'Wing Cmrd.', 'Comdr.']
        GovtTitles = ['District Judge', 'Chairman', 'Charleston Police Chief', 'Police Chief', 'Deputy',
                      'United States', 'New York State', 'State', 'Vice President', 'President', 'Prime', 'Economy',
                      'Commerce Secretary', 'Minister', 'Governor', 'Gov.', 'Chief', 'Justice', 'Federal District',
                      'Judge', 'Senator', 'Representative', 'Sheriff', 'Assemblyman', 'Assemblywoman',
                      'Assembly Speaker', 'Mayor', 'Mayoress', 'City Councilman', 'Councilman', 'Councilwoman']
        prefixToTitles = ['Former', 'Retired', 'Sir']
        randomExtra = ['Newsday']

        JobTitles = prefixToTitles + randomExtra + ReligiousTitles + MilitaryTitles + ProfessionalTitles + GovtTitles

        # w1 is above titles but each only 1 word, using the root (Admiral rather than Grand Admiral)...never got around to using it
        w1ReligiousTitles = ['Rabbi', 'Elder', 'Beatitude', 'Rev.', 'Reverend', 'Father', 'Cardinal', 'Msgr.',
                             'Monsignor', 'Auxiliary', 'Bishop', 'Archbishop']
        # problem dont extract Marshal because Marshall is a name
        w1MilitaryTitles = ['Capt.', 'Captain', 'Comdr.', 'Marshal', 'Adm.', 'Admiral', 'Commodore', 'Sgt.',
                            'Officer', 'Lt.', 'Lieut.', 'Maj.', 'Major', 'Col.', 'Colonel', 'Brig.', 'Brigadier',
                            'General', 'Gen.', 'Cmrd.']
        w1ProfessionalTitles = ['Doctor', 'Dr.', 'Professor', 'Prof', 'Prof.']
        w1GovtTitles = ['Chairman', 'President', 'Secretary', 'Minister', 'Governor', 'Gov.', 'Justice', 'Judge',
                        'Senator', 'Representative', 'Rep.', 'Sheriff', 'Assemblyman', 'Assemblywoman', 'Speaker',
                        'Mayor', 'Mayoress', 'Councilman', 'Councilwoman']
        w1prefixToTitles = ['Former', 'Retired', 'Sir']

        name_suffixes = ['Jr.', 'Sr.', 'III', 'II', '2d', '3d', '4d', '2D', '3D', '2nd', '3rd', '4th', '5th', '6th']

        lowercase_nameparts = ['lvarez', 'del', 'des', 'deM.', 'den', 'y', 'de', 'a', 'da', 'von', 'van', 'bin',
                               'ibn', 'dos', 'la', 'vom',
                               'der', 'di', 'du', 'taix', 'zu']


        tsn = self["title"]
        fsn = self["firstSentence"]

        for pp in pats:
            tsn = re.split(pp, tsn, flags=re.IGNORECASE)[0]
            fsn = re.split(pp, fsn, flags=re.IGNORECASE)[0]

        #      fsnc = fsn.count(' ')
        #      if fsnc > 8:
        #          print(fsnc,fsn)

        tsn = removejunk(tsn)
        fsn = removejunk(fsn)

        tsn = addspaceafterperiod(tsn)
        fsn = addspaceafterperiod(fsn)

        ret['JobTitleInTitle'] = ''
        ret['JobTitleInFS'] = ''
        for jj in JobTitles:
            #    if len(tsn) > len(jj):
            if (tsn.startswith(jj) or tsn.startswith(jj.upper())):  # and tsn[len(jj)] == ' ':

                tsn = tsn[len(jj) + 1:]
                if len(ret['JobTitleInTitle']) == 0:
                    ret['JobTitleInTitle'] = jj
                else:
                    ret['JobTitleInTitle'] = ret['JobTitleInTitle'] + ' ' + jj

            #   if len(fsn) > len(jj):
            if fsn.startswith(jj):  # and fsn[len(jj)] == ' ':

                fsn = fsn[len(jj) + 1:]
                if len(ret['JobTitleInFS']) == 0:
                    ret['JobTitleInFS'] = jj
                else:
                    ret['JobTitleInFS'] = ret['JobTitleInFS'] + ' ' + jj

        title_stet = {29087, 33001}  # King X II of Samoa, of Morocco ... stet
        ret['nameSuffixInTitle'] = ''
        tsn_o = tsn

        # checked output dont see any double suffixes
        # deletes text that comes after the suffix, this is always extraneous info like "Bill Smith Jr. manufacturer"
        # suffix is later added back
        for jj in name_suffixes:
            jjloc = max(tsn.find(jj), tsn.find(jj.upper()))
            if jjloc != -1:
                #       print(self["id"],tsn[jjloc - 1] == ' ') #jjloc,tsn[:jjloc - 1],'jj',tsn[jjloc - 1:],tsn)
                if tsn[jjloc - 1] == ' ' and self['id'] not in title_stet:

                    ret['nameSuffixInTitle'] = jj
                    tsn = tsn[:jjloc - 1]

        # checked output found same 2 kings as in titles, also cases of WWII
        fs_stet = {29087, 33001, 14438}
        ret['nameSuffixInFS'] = ''
        fsn_o = fsn

        for jj in name_suffixes:
            jjloc = max(fsn.find(jj), fsn.find(jj.upper()))
            if jjloc != -1:
                if fsn[jjloc - 1] == ' ' and self['id'] not in fs_stet and 'World War II' not in fsn:

                    ret['nameSuffixInFS'] = jj
                    fsn = fsn[:jjloc - 1]

        # since no conflicting suffixes, create a common suffix to be rejoined with name later
        ret["nameSuffix"] = ''
        if not (ret['nameSuffixInTitle'] == '' and ret['nameSuffixInFS'] == ''):
            if ret['nameSuffixInTitle'] != '' and ret['nameSuffixInFS'] != '':

                if ret['nameSuffixInTitle'] != ret['nameSuffixInFS'] == '':
                    print('NEQ:', ret['nameSuffixInTitle'], ret['nameSuffixInFS'] == '')
                    # didnt find any

                else:
                    ret["nameSuffix"] = ret["nameSuffixInTitle"]
            elif ret['nameSuffixInTitle'] == '' and ret['nameSuffixInFS'] != '':

                #            print("f only",fsn,ret["nameSuffixInFS"])
                ret["nameSuffix"] = ret["nameSuffixInFS"]
            elif ret['nameSuffixInTitle'] != '' and ret['nameSuffixInFS'] == '':

                ret["nameSuffix"] = ret["nameSuffixInTitle"]
        #            print('t only',tsn,ret["nameSuffixInTitle"])

        # check if all words in tsn start with caps, if it is, save it as candidate for best name even though may not be contained in fsn
        # though note that some titles all letters are caps so for them this is not a good test, see below
        tsn_split = tsn.split(' ')

        tsn_all_words_start_caps = True
        t_nUpper = 0
        if tsn_split is None:
            tsn_all_words_start_caps = False
        else:
            for w in tsn_split:
                t_w_is_OK = False
                for nonupper in lowercase_nameparts:
                    if w == nonupper:
                        t_w_is_OK = True

                    if not t_w_is_OK and len(w) > 0:
                        if w[0].isupper() or w[0] == '(':
                            t_w_is_OK = True

                if not t_w_is_OK:
                    tsn_all_words_start_caps = False
        if tsn_all_words_start_caps:

            ret["title comma literal is name-like phrase"] = True
            ret["title comma literal phrase"] = tsn
        else:
            ret["title comma literal is name-like phrase"] = False
            ret["title comma literal phrase"] = ''

        # check if words in fsn all start with caps
        # useful test though can fail, for example in "He died", He is fsn
        fsn_split = fsn.split(' ')

        fsn_all_words_start_caps = True
        f_nUpper = 0
        if fsn_split is None:
            fsn_all_words_start_caps = False
        else:
            for w in fsn_split:
                f_w_is_OK = False
                for nonupper in lowercase_nameparts:
                    if w == nonupper:
                        f_w_is_OK = True

                    if not f_w_is_OK and len(w) > 0:
                        if w[0].isupper() or w[0] == '(':
                            f_w_is_OK = True

                if not f_w_is_OK:
                    fsn_all_words_start_caps = False

        if fsn_all_words_start_caps:

            ret["fs comma literal is name-like phrase"] = True
            ret["fs comma literal phrase"] = fsn
        else:
            ret["fs comma literal is name-like phrase"] = False
            ret["fs comma literal phrase"] = ''

        # check if two phrases are exact match
        ret["pure comma literal match"] = False
        ret["pure comma literal name"] = ''
        if tsn.lower() == fsn.lower():
            # ELIMINATE TEST OF WHETHER STANFORD THINKS ITS A PERSON
            #           if tsn.lower() == self["stanford_PERSON"][0].lower():

            ret["pure comma literal match"] = True
            ret["pure comma literal name"] = fsn
            if ret['nameSuffix'] != '':
                ret["pure comma literal name"] = ret["pure comma literal name"] + ' ' + ret["nameSuffix"]

        # check how many words in tsn and fsn are the same (how big is overlap) and where these overlaps start and stop
        # if have repeat in fsn (Woo Woo Smith) same word will match multiple times
        # but checked these cases, all involve match of name and corresponding initial
        # (Jim J. Smith and J. J. Smith match 3 times not 2, which is OK; but Albert J. Smith and A.A. Smith would match 2 times)

        # obit[f_t_meld] holds matching elements in 2 phrases
        ret["t nwords"] = tsn.count(' ') + 1
        ret["fs nwords"] = fsn.count(' ') + 1
        ret["t_fs n overlaps"] = 0
        firstmatch_t = -1
        lastmatch_t = -1
        firstmatch_f = -1
        lastmatch_f = -1
        no_prior_matches = True
        for i, t_word in enumerate(tsn_split):
            this_t_word_notmatchedyet = True
            for j, fs_word in enumerate(fsn_split):
                if this_t_word_notmatchedyet:
                    if general_match(t_word, fs_word) or (
                            no_prior_matches and match_on_initial(t_word, fs_word)):
                        if no_prior_matches:
                            firstmatch_t = i
                            firstmatch_f = j
                            no_prior_matches = False

                        #         if match_on_initial(t_word,fs_word) and tsn != fsn:

                        #           print(tsn,fsn)
                        lastmatch_t = i
                        lastmatch_f = j

                        this_t_word_notmatchedyet = False
                        
        ret["literal last t element match"] = False
        if lastmatch_t == len(tsn_split) - 1:
            ret["literal last t element match"] = True
        ret["literal last f element match"] = False
        if lastmatch_f == len(fsn_split) - 1:
            ret["literal last f element match"] = True
        ret['more_expansive'] = ''
        ret['less_expansive'] = ''
        if firstmatch_t != -1 and lastmatch_t != firstmatch_t:
            if firstmatch_f > lastmatch_f:  # this never occurs for _t only _f
                ret['more_expansive'] = tsn_split[firstmatch_t:lastmatch_t + 1]
                ret['less_expansive'] = fsn_split[lastmatch_f] + fsn_split[firstmatch_f]
            elif lastmatch_t - firstmatch_t > lastmatch_f - firstmatch_f:
                ret['more_expansive'] = tsn_split[firstmatch_t:lastmatch_t + 1]
                ret['less_expansive'] = fsn_split[firstmatch_f:lastmatch_f + 1]
            else:
                ret['less_expansive'] = tsn_split[firstmatch_t:lastmatch_t + 1]
                ret['more_expansive'] = fsn_split[firstmatch_f:lastmatch_f + 1]

            n_notupper = 0
            l_parts = 0
            nlower = 0
            if len(ret['less_expansive']) > 0:	
                for w in ret['less_expansive']:		
                    if len(w) > 0:  		
                        if not w[0].isupper() and w[0] != '(':		
                            n_notupper += 1		
                        if w in lowercase_nameparts:
                            l_parts += 1
                nlower = n_notupper - l_parts
                if nlower > 0:
                    ret['less_expansive'] = ''

            n_notupper = 0
            l_parts = 0
            nlower = 0
            if len(ret['more_expansive']) > 0:
                nlower = n_notupper - l_parts
                if nlower > 0:
                    ret['more_expansive'] = ''
                    # phrase should be name-like with all words starting with capitals except known lower-case name parts like 'de'
                    #     print(ret['more_expansive'],n_notupper,l_parts,'\n')


            if ret['less_expansive'] != '':
                ret['less_expansive'] = ' '.join(ret['less_expansive'])
            if ret['more_expansive'] != '':
                ret['more_expansive'] = ' '.join(ret['more_expansive'])

            if ret['nameSuffix'] != '':
                ret['less_expansive'] = ret['less_expansive'] + ' ' + ret['nameSuffix']
                ret['more_expansive'] = ret['more_expansive'] + ' ' + ret['nameSuffix']

        ret["f contains t"] = False
        ret["t contains f"] = False
        ret['t and f all words have match'] = False
        if ret["t_fs n overlaps"] == ret["t nwords"]:
            ret["f contains t"] = True

        if ret["t_fs n overlaps"] == ret["fs nwords"]:
            ret["t contains f"] = True

        if ret["t contains f"] and ret["f contains t"]:
            ret["t and f all words have match"] = True


        ret["t contains f name"] = ''
        ret["f contains t name"] = ''
        if ret["t contains f"] and ret["title comma literal is name-like phrase"]:
            ret["t contains f name"] = tsn
        if ret["t contains f name"] != '' and ret["nameSuffix"] != '':
            ret["t contains f name"] = ret["t contains f name"] + ' ' + ret["nameSuffix"]

        if ret["f contains t"] and ret["fs comma literal is name-like phrase"]:
            ret["f contains t name"] = fsn
        if ret["f contains t name"] and ret["nameSuffix"] != '':
            ret["f contains t name"] = ret["f contains t name"] + ' ' + ret["nameSuffix"]

        # eliminate matches when either the fs or title is corrupted, since they often produce misleading false positives
        # better here to let the uncorrupted entry stand, or fix manually

        if self['title_corrupted'] or self['fs_corrupted']:
            ret['more_expansive'] = ''
            ret['less_expansive'] = ''
            ret['f contains t'] = False
            ret['t contains f'] = False
            ret['t contains f name'] = ''
            ret['f contains t name'] = ''

        # ret["f contains t"] and ret["t contains f'] is based on exact matches between words
        # but involve general matching which treats initials as extending to any word that starts with the same letter
        # f_contains_t and t_contains_f is based on words being within other words, so counts not only eact matches but partilal inclusions (like Jim and Jimmy)

        # check if tsn contains fsn (all words in fsn are in tsn)
        # set the name to the containing one, on the theory that this will get a fuller name including middle name etc;
        # but note it will also get the name that includes extraneous material like job title not caught in above list,
        ret["pure split tsn contains fsn match"] = False
        ret["pure split tsn contains fsn name"] = ''
        t_contains_f = True
        for namepart in fsn_split:
            if namepart.lower() not in tsn.lower():
                t_contains_f = False

        if t_contains_f:

            ret["pure split tsn contains fsn match"] = True
            ret["pure split tsn contains fsn name"] = tsn
            if tsn_all_words_start_caps:
                ret["pure split tsn contains fsn name"] = tsn
            else:
                ret["pure split tsn contains fsn name"] = fsn

        # check if fsn contains tsn (all words in tsn are in fsn)
        ret["pure split comma literal match"] = False
        ret["pure split comma literal name"] = ''
        f_contains_t = True
        for namepart in tsn_split:
            if namepart.lower() not in fsn.lower():
                f_contains_t = False
        if f_contains_t:

            ret["pure split comma literal match"] = True
            if fsn_all_words_start_caps:
                ret["pure split comma literal name"] = fsn
            else:
                ret["pure split comma literal name"] = tsn








        # -------------------------------------------------------

        # create t_pnames and FS_pnames from stanford_PERSON_title and stanford_PERSON
        # make them all uppercase since stanford_PERSON_title is already all uppercase (dont know why, would be easier if not).
        # dont make all upper case instead compare via upper() when needed
        # for fs, use only 2 part names since the construction of stanford_fs includes lots of single names from later in the fb

        # here use coder.obituaries rather than obits_w_tok, the hard work of tagging has already been done in forming stanford_PERSON_title

        cc = 0
        counter = 0
        counter2 = 0

        ccq = 0

        ret["t_pnames"] = []
        for name in self["stanford_PERSON_title"]:
            ret["t_pnames"].append(name)

        ret["stanford_fs"] = [x for x in self["stanford_PERSON"] if x in self["firstSentence"]]
        ret["FS_pnames"] = []
        for name in ret["stanford_fs"]:
            if ' ' in name:
                ret["FS_pnames"].append(name)

        ret["1st fB name"] = ''
        if len(ret["FS_pnames"]) > 0:
            ret["1st fB name"] = ret["FS_pnames"][0]
        elif len(self["stanford_PERSON"]) > 0:
            ret["1st fB name"] = self["stanford_PERSON"][0]

        of_start = ret["1st fB name"].find(" of ")
        if of_start != -1:
            #    print(self["id"],ret["1st fB name"])
            if not (ret["1st fB name"].find("Earl") == 0 or ret["1st fB name"].find("Duke") == 0 or ret[
                "1st fB name"].find("Lord") == 0):
                ret["1st fB name"] = ret["1st fB name"][0:of_start]
        #       print(ret["1st fB name"])

        # didnt find any title names with of
        if len(ret["t_pnames"]) > 0:
            of_start = ret["t_pnames"][0].find(" of ")
            if of_start != -1:
                #          print(self["id"],ret["t_pnames"][0])
                if not (ret["t_pnames"][0].find("Earl") == 0 or ret["t_pnames"][0].find("Duke") == 0 or
                        ret["t_pnames"][0].find("Lord") == 0):
                    ret["t_pnames"][0] = ret["t_pnames"][0][0:of_start]


        # for a good number of the names cutoff at a middle initial, there is a following name in the list that gives the last name;
        # but for many others there isnt so cant count on this

        ret["mp_stanford_PERSON"] = []
        ret["1part pnames fB"] = []
        for name in self["stanford_PERSON"]:
            if ' ' in name:
                ret["mp_stanford_PERSON"].append(name)

            else:
                ret["1part pnames fB"].append(name)

        # exact match of first stanford-recognized person name, title and fs
        # not defined by comma format name may be anywhere in fs or title
        # looked at multi person cases, first one is almost always the obituaried ("Jim Smith, who wrote about William Tell")

        # already effectively uses 1st fB name

        permatch = 0
        ppermatch = 0

        c3 = 0

        ret["s_f pname match"] = False
        if len(ret["FS_pnames"]) > 0 and len(ret["t_pnames"]) > 0:
            if ret["FS_pnames"][0].lower() == ret["t_pnames"][0].lower():
                permatch += 1
                ret["s_f pname match"] = True
        elif len(self["stanford_PERSON"]) > 0 and len(ret["t_pnames"]) > 0:
            if self["stanford_PERSON"][0].lower() == ret["t_pnames"][0].lower():
                ppermatch += 1
                ret["s_f pname match"] = True

        # s_p matches are good, only problem is when stanford name has deleted a component of name so shorter than title phrase
        # which also happens with 0th pname match
        # use s_p pname match instead of 0th pname match



        # generate last names in t and fs

        from nlp import HumanName

        nlookedat = 0

        ret["t_lastnames"] = []
        if len(ret["t_pnames"]) > 0:
            nlookedat += 1
            for k, pname in enumerate(ret["t_pnames"]):
                lastname = HumanName(ret["t_pnames"][k]).last
                ret["t_lastnames"].append(lastname)

        ret["FS_lastnames"] = []
        if len(ret["FS_pnames"]) > 0:
            for k, pname in enumerate(ret["FS_pnames"]):
                lastname = HumanName(ret["FS_pnames"][k]).last
                ret["FS_lastnames"].append(lastname)

        # last name matches of first appearing t and fs people names

        lastnamematch = 0

        ret["matched lastname1"] = ''
        ret["matched pname1"] = "not found"
        ret["0th lastname match"] = False
        if len(ret["FS_pnames"]) > 0 and len(ret["t_pnames"]) > 0:
            if ret["t_lastnames"][0].upper() == ret["FS_lastnames"][0].upper():
                lastnamematch += 1
                ret["0th lastname match"] = True
                # uses total length of namestring in characters, longer one generally includes more detail
                # note that one may involve a typo, here not trying to deal with that
                if len(ret["FS_pnames"][0]) > len(ret["t_pnames"][0]):
                    ret["matched lastname1"] = ret["FS_pnames"][0]
                else:
                    ret["matched lastname1"] = ret["t_pnames"][0]

        # identify cases where have a name in title but not in fs, or a name in fs but not in title, or in died but not title or fs

        titlesolo = 0
        fs_solo = 0
        diedsolo = 0

        ret["title solo"] = False
        ret["FS solo"] = False
        ret["died solo"] = False
        if (len(ret["t_pnames"]) > 0 and ret["1st fB name"] == ''):
            titlesolo += 1
            ret['title solo'] = True
        elif len(ret["t_pnames"]) == 0 and ret["1st fB name"] != '':
            ret['FS solo'] = True
            fs_solo += 1
        elif self["name_from_died_sent"] is not None:
            if (len(ret["t_pnames"]) == 0 and len(ret["FS_pnames"]) == 0) and len(
                    self["name_from_died_sent"]) > 0:
                ret['died solo'] = True
                diedsolo += 1

        # generate most common names (names that most frequently appear in the fullBody as most common element, most common multipart element, most common single part element )

        ret["name_mostcommon_fB"] = ''
        ret["mpname_mostcommon_fB"] = ''
        ret["1pname_mostcommon_fB"] = ''
        if self["stanford_PERSON"] is not None:
            if len(self["stanford_PERSON"]) > 0:
                ret["name_mostcommon_fB"] = most_freq_element(self["stanford_PERSON"])
                ret["freq of mostcommon_fB"] = self["stanford_PERSON"].count(ret["name_mostcommon_fB"])
        if ret["mp_stanford_PERSON"] is not None:
            if len(ret["mp_stanford_PERSON"]) > 0:
                ret["mpname_mostcommon_fB"] = most_freq_element(ret["mp_stanford_PERSON"])
                ret["freq of mp mostcommon_fB"] = ret["mp_stanford_PERSON"].count(ret["mpname_mostcommon_fB"])

        if ret["1part pnames fB"] is not None:
            if len(ret["1part pnames fB"]) > 0:
                ret["1pname_mostcommon_fB"] = most_freq_element(ret["1part pnames fB"])
                ret["freq of 1part fB"] = ret["1part pnames fB"].count(ret["1pname_mostcommon_fB"])

        ret["flit in multi mc"] = False
        ret["flit multi mc name"] = "Not Found"
        ret["flit words"] = 0
        ret["f_mc lit laps"] = 0
        if ret['fs comma literal phrase'] != '':
            fsname = ret["fs comma literal phrase"].split(' ')

            for nameparts in fsname:
                for np in ret["name_mostcommon_fB"].split():
                    if nameparts.lower() == np.lower():
                        ret["f_mc lit laps"] += 1

                for np2 in ret["mpname_mostcommon_fB"].split():
                    if nameparts.lower() == np2.lower():
                        ret["f_mc lit laps"] += 1

                if nameparts.lower() == ret["1pname_mostcommon_fB"].lower():
                    ret["f_mc lit laps"] += 1

            if ret["f_mc lit laps"] > 0:
                ret["flit in multi mc"] = True
                ret["flit multi mc name"] = ret["fs comma literal phrase"]
                ret["flit words"] = ret["flit multi mc name"].count(' ') + 1

        ret["tlit in multi mc"] = False
        ret["tlit multi mc name"] = "Not Found"
        ret["tlit words"] = 0
        ret["t_mc lit laps"] = 0
        if ret['title comma literal phrase'] != '':
            fsname = ret["title comma literal phrase"].split(' ')

            for nameparts in fsname:
                for np in ret["name_mostcommon_fB"].split():
                    if nameparts.lower() == np.lower():
                        ret["t_mc lit laps"] += 1

                for np2 in ret["mpname_mostcommon_fB"].split():
                    if nameparts.lower() == np2.lower():
                        ret["t_mc lit laps"] += 1

                if nameparts.lower() == ret["1pname_mostcommon_fB"].lower():
                    ret["t_mc lit laps"] += 1

            if ret["t_mc lit laps"] > 0:
                ret["tlit in multi mc"] = True
                ret["tlit multi mc name"] = ret["title comma literal phrase"]
                ret["tlit words"] = ret["tlit multi mc name"].count(' ') + 1



        ret["fsname split in multi mc"] = False
        ret["fmatched multi mc name"] = "Not Found"
        ret["fsn words"] = 0
        ret["f_mc laps"] = 0
        if len(self['stanford_PERSON']) > 0:
            fsname = ret["1st fB name"].split(' ')

            for nameparts in fsname:
                for np in ret["name_mostcommon_fB"].split():
                    if nameparts.lower() == np.lower():
                        ret["f_mc laps"] += 1

                for np2 in ret["mpname_mostcommon_fB"].split():
                    if nameparts.lower() == np2.lower():
                        ret["f_mc laps"] += 1

                if nameparts.lower() == ret["1pname_mostcommon_fB"].lower():
                    ret["f_mc laps"] += 1

            if ret["f_mc laps"] > 0:
                ret["fsname split in multi mc"] = True
                ret["fmatched multi mc name"] = ret["1st fB name"]
                ret["fsn words"] = ret["fmatched multi mc name"].count(' ') + 1


        # match most common multipart name in fB with tpname, if the former contains the latter

        ret["tpname split in multi mc"] = False
        ret["tmatched multi mc name"] = "Not Found"
        ret["tpn words"] = 0
        ret["t_mc laps"] = 0
        if len(self["stanford_PERSON_title"]) > 0 and len(self['stanford_PERSON']) > 0:
            ptname = self["stanford_PERSON_title"][0].split(' ')

            for nameparts in ptname:
                for np in ret["name_mostcommon_fB"].split():
                    if nameparts.lower() == np.lower():
                        ret["t_mc laps"] += 1
                for np2 in ret["mpname_mostcommon_fB"].split():
                    if nameparts.lower() == np2.lower():
                        ret["t_mc laps"] += 1
                if nameparts.lower() == ret["1pname_mostcommon_fB"].lower():
                    ret["t_mc laps"] += 1

            if ret["t_mc laps"] > 0:
                ret["tpname split in multi mc"] = True
                ret["tmatched multi mc name"] = self["stanford_PERSON_title"][0]
                ret["tpn words"] = ret["tmatched multi mc name"].count(' ') + 1


        # find best matching multi mc
        laps = [ret['t_mc laps'], ret['t_mc lit laps'], ret['f_mc laps'], ret['f_mc lit laps']]
        words = [ret['tpn words'], ret['tlit words'], ret['fsn words'], ret['flit words']]
        matches = [ret['tmatched multi mc name'], ret['tlit multi mc name'], ret['fmatched multi mc name'],
                   ret['flit multi mc name']]
        maxlaps = max(laps)
        maxlaps_index = laps.index(maxlaps)
        nmaxlaps = laps.count(maxlaps)
        maxwords = max(words)
        maxwords_index = words.index(maxwords)
        nmaxwords = words.index(maxwords)

        ret["best_mc_fit"] = ''
        if nmaxlaps == 1:
            ret["best_mc_fit"] = matches[maxwords_index]
        else:
            for i in range(len(laps) - 1, -1, -1):
                if laps[i] < maxlaps:
                    words.pop(i)
                    matches.pop(i)
            maxwords2 = max(words)
            maxwordsindex2 = words.index(maxwords2)
            ret["best_mc_fit"] = matches[maxwordsindex2]

        if ret["best_mc_fit"] == 'Not Found':
            ret["best_mc_fit"] = ''
        # this happens when all 4 matches are 'Not Found'










        tlitcorrect = {1747, 27219, 54615}

        qmarks = {}

        # in some obits only Mr. is used; when sufficiently high profile I googled, otherwise left as Mr if inspection of fullBody didnt provide a name
        # in one obit there is no name at all

        ret["human coded name"] = "not coded"
        if self["id"] in tlitcorrect:
            ret["human coded name"] = ret["title comma literal phrase"]
        if self["id"] == 24788:
            ret["human coded name"] = "Gerry Davis"
        if self["id"] == 26832:
            ret["human coded name"] = "William Shakespeare"
        if self["id"] == 28215:
            ret["human coded name"] = "Janet Reno"
        if self["id"] == 28386:
            ret["human coded name"] = "China Machado"
        if self["id"] == 60740:
            ret["human coded name"] = "Robert Henry Dicke"
        if self["id"] == 18956:
            ret["human coded name"] = "John M. Ashbrook"
        if self["id"] == 22109:
            ret["human coded name"] = "Henry Miller"
        if self["id"] == 28386:
            ret["human coded name"] = "China Machado"
        if self["id"] == 14440:
            ret["human coded name"] = "Sonia Orwell"
        if self["id"] == 14444:
            ret["human coded name"] = "Sonia Orwell"
        if self["id"] == 1764:
            ret["human coded name"] = "A.J.P. Taylor"
        if self["id"] == 38228:
            ret["human coded name"] = "Mr Brady"
        if self["id"] == 37480:
            ret["human coded name"] = "Mr Hochschild"
        if self["id"] == 22392:
            ret["human coded name"] = "James B. Longley"
        if self["id"] == 22440:
            ret["human coded name"] = "Gower Champion"
        if self["id"] == 23061:
            ret["human coded name"] = "Pat Summitt"
        if self["id"] == 28313:
            ret["human coded name"] = "Burton J. Lee III"
        if self["id"] == 28339:
            ret["human coded name"] = "Nancy Mairs"
        # read obit no name in it
        if self["id"] == 23805:
            ret["human coded name"] = '<No Name Provided in Obituary>'
        # only obit not to receive a best name
        if self["id"] == 201:
            ret["human coded name"] = "Margaret, Duchess of Argyll"
        if self["id"] == 17305:
            ret["human coded name"] = "Anne deBonneville (Bonnie) Young"
        if self["id"] == 23765:
            ret["human coded name"] = "Mr Chandris"
        if self["id"] == 28256:
            ret["human coded name"] = "Denton A. Cooley"
        if self["id"] == 32368:
            ret["human coded name"] = "King Hussein of Jordan"
        if self["id"] == 3239:
            ret["human coded name"] = "Philip (Slim) Connelly"
        if self["id"] == 36445:
            ret["human coded name"] = "Kunio Sakan"
        if self["id"] == 41831:
            ret["human coded name"] = "Thomas P. (Tip) O'Neill Jr."
        if self["id"] == 47713:
            ret["human coded name"] = "Francis Lazarro (Frank) Rizzo"
        if self["id"] == 48061:
            ret["human coded name"] = "Larkin Smith"
        if self["id"] == 55257:
            ret["human coded name"] = "Mr Gallagher"
        if self["id"] == 59640:
            ret["human coded name"] = "Melber Chambers"
        if self["id"] == 45740:
            ret["human coded name"] = "Diana, Princess of Wales"
        if self["id"] == 23288:
            ret["human coded name"] = "Donald A. Henderson"
        if self["id"] == 32435:
            ret["human coded name"] = "Wilmer (Vinegar Bend) Mizell"
        if self["id"] == 12161:
            ret["human coded name"] = "Richard Blackwell"
        if self["id"] == 28304:
            ret["human coded name"] = "Grant Tinker"
        if self["id"] == 36756:
            ret["human coded name"] = "Ahmed Sekou Toure"
        if self["id"] == 50619:
            ret["human coded name"] = "Mario Soares"
        if self["id"] == 6546:
            ret["human coded name"] = "Ed Williams"
        if self["id"] == 12734:
            ret["human coded name"] = "Major Harris"
        if self["id"] == 13711:
            ret["human coded name"] = "Johann-Adolf Count van Kielmansegg"
        if self["id"] == 141:
            ret["human coded name"] = "Vincent W. Foster, Jr."
        if self["id"] == 14241:
            ret["human coded name"] = "Edmund F. McNally"
        if self["id"] == 14256:
            ret["human coded name"] = "William B. Grey"

        if self["id"] == 22368:
            ret["human coded name"] = "Frank Van Dyk"
        if self["id"] == 23834:
            ret["human coded name"] = "Charles P. Buchanan"
        if self["id"] == 25212:
            ret["human coded name"] = "C. James Fleming Jr."
        if self["id"] == 26279:
            ret["human coded name"] = "Howard K. Siebens"
        if self["id"] == 27738:
            ret["human coded name"] = "Henri Cardinal de Lubac"

        if self["id"] == 29714:
            ret["human coded name"] = "Annie Henderson"
        if self["id"] == 34450:
            ret["human coded name"] = "John N. Mitchell"
        if self["id"] == 30209:
            ret["human coded name"] = "Ryutaro Hashimoto"
        if self["id"] == 52740:
            ret["human coded name"] = "Stephen Chandler"
        if self["id"] == 54205:
            ret["human coded name"] = "Roger E. Ailes"
        if self["id"] == 23834:
            ret["human coded name"] = "Charles P. Buchanan"
        if self["id"] == 25212:
            ret["human coded name"] = "C. James Fleming Jr."
        if self["id"] == 26279:
            ret["human coded name"] = "Howard K. Siebens"
        if self["id"] == 27738:
            ret["human coded name"] = "Henri Cardinal de Lubac"

        if self["id"] == 28404:
            ret["human coded name"] = "Miruts Yifter"
        if self["id"] == 29798:
            ret["human coded name"] = "Eva Narcissus (Little Eva) Boyd"
        if self["id"] == 30944:
            ret["human coded name"] = "Bobbie Nudie"
        if self["id"] == 35599:
            ret["human coded name"] = "Imad Mugniyah"
        if self["id"] == 55543:
            ret["human coded name"] = "Katie ter Horst"
        if self["id"] == 42344:
            ret["human coded name"] = "Frederick C. Kempner"
        if self["id"] == 42658:
            ret["human coded name"] = "Lawrence J. Washington"
        if self["id"] == 44247:
            ret["human coded name"] = "Judith A. Resnick"
        if self["id"] == 40290:
            ret["human coded name"] = "Gladys M. Peare"
        if self["id"] == 40977:
            ret["human coded name"] = "Ruth Kornblum"
        if self["id"] == 42302:
            ret["human coded name"] = "Kent Harrison"
        if self["id"] == 42338:
            ret["human coded name"] = "R. J. Maughan"
        if self["id"] == 42346:
            ret["human coded name"] = "Charles S.H. Hunter Jr."
        if self["id"] == 44247:
            ret["human coded name"] = "Gregory B. Jarvis"
        if self["id"] == 40570 or self["id"] == 40571:
            ret["human coded name"] = "Leonid Brezhnev"
        if self["id"] == 2468:
            ret["human coded name"] = "Elizabeth Taylor"
        if self["id"] == 33575:
            ret["human coded name"] = "Tom Petty"
        if self["id"] == 3555:
            ret["human coded name"] = "John Elias Karlin"
        if self["id"] == 25909:
            ret["human coded name"] = "William Robertson Davies"





        # now prune it!

        tokeep = [
            "human coded name", "pure comma literal match", "fs comma literal phrase",
            "1st fB name", "title comma literal phrase", "t_pnames",
            "pure comma literal name", "more_expansive", "t contains f name",
            "f contains t name", "1st fB name", "matched lastname1", "best_mc_fit",
            "t_pnames", "1st fB name", "title comma literal phrase", "fs comma literal phrase",
            "s_f pname match", "0th lastname match", "title solo", "FS solo",
            "title comma literal is name-like phrase", "fs comma literal is name-like phrase"
        ]

        for k in list(ret.keys()):
            if k not in tokeep:
                del ret[k]



        return ret




class best_name(g.PropertyCoder):
    def run(self):

        best_name = 'Not Found'
        name_method = 'No Method'
        if self["not_obit"] == False:

            if self['name_prior']['human coded name'] != "not coded":
                name_method = 'human coded'
                best_name = self['name_prior']['human coded name']

            elif self['title_corrupted'] and self['name_prior']['fs comma literal is name-like phrase']:
                name_method = 'fs name-like phrase'
                best_name = self['name_prior']['fs comma literal phrase']

            elif self['title_corrupted'] and self['name_prior']['FS solo']:
                name_method = 'FS solo'
                best_name = self['name_prior']['1st fB name']

            elif self['fs_corrupted'] and self['name_prior']['title comma literal is name-like phrase']:
                name_method = 'title name-like phrase'
                best_name = self['name_prior']['title comma literal phrase']

            elif self['fs_corrupted'] and self['name_prior']['title solo']:
                name_method = 'title solo'
                best_name = self['name_prior']['t_pnames'][0]

            elif self['name_prior']['pure comma literal match']:
                name_method = 'pure comma literal match'
                best_name = self['name_prior']["pure comma literal name"]

            elif self['name_prior']['more_expansive'] != '':
                name_method = 'more_expansive'
                best_name = self['name_prior']["more_expansive"]

            elif self['name_prior']['t contains f name'] != '':
                name_method = 't contains f'
                best_name = self['name_prior']["t contains f name"]

            elif self['name_prior']['f contains t name'] != '':
                name_method = 'f contains t'
                best_name = self['name_prior']["f contains t name"]

            elif (self['name_prior']["s_f pname match"]):
                name_method = '0th pname match'
                best_name = self['name_prior']["1st fB name"]

            elif self['name_prior']['0th lastname match']:
                name_method = '0th lastname match'
                best_name = self['name_prior']["matched lastname1"]

            elif self['name_prior']['best_mc_fit'] != '':
                name_method = 'best_mc_fit'
                best_name = self['name_prior']['best_mc_fit']

            elif self['name_prior']['title solo']:
                name_method = 'title solo'
                best_name = self['name_prior']["t_pnames"][0]

            elif self['name_prior']['FS solo']:
                name_method = 'FS solo'
                best_name = self['name_prior']["1st fB name"]

            elif self['name_prior']['title comma literal is name-like phrase']:
                name_method = 'title name-like phrase'
                best_name = self['name_prior']['title comma literal phrase']

            elif self['name_prior']['fs comma literal is name-like phrase']:
                name_method = 'fs name-like phrase'
                best_name = self['name_prior']['fs comma literal phrase']


        nwords = best_name.count(' ') + 1
        if nwords == 1 and name_method == '0th pname match' and self['name_prior']['best_mc_fit'].count(' ') + 1 > 1:
            name_method = 'best_mc_fit'
            best_name = self['name_prior']['best_mc_fit']

        self['name_method'] = name_method
        return best_name
