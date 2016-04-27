#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

try:
    import requests
except ImportError:
    print ImportError
    print "please try 'sudo pip install requests' to fix it !"

try:
    import BeautifulSoup
except ImportError:
    print ImportError
    print "please try 'sudo pip install BeautifulSoup' to fix it !"


class V2EX:
    """auto checkin for V2EX and get rewards"""
    username = ''
    password = ''
    signin_url = "https://www.v2ex.com/signin"
    award_url = "https://www.v2ex.com/mission/daily"
    referer_url = "https://www.v2ex.com/mission/daily"
    main_url = "https://www.v2ex.com"
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:23.0) Gecko/20100101 Firefox/23.0"
    post_headers = {"User-Agent": user_agent,
                    "Referer": signin_url}
    headers = {"User-Agent": user_agent}
    checkin_headers = {"User-Agent": user_agent,
                       "Referer": referer_url}
    v2ex_session = {}
    main_soup = {}

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.v2ex_session = requests.Session()
        self.main_soup = BeautifulSoup.BeautifulSoup()
        print datetime.datetime.now(), " : start 'V2EX' checkin for  ", self.username

    def login(self):
        # get login_info random 'once' value
        v2ex_main_req = self.v2ex_session.get(
            self.signin_url, headers=self.headers)
        v2ex_main_tag = BeautifulSoup.BeautifulSoup(v2ex_main_req.content)
        form_tag = v2ex_main_tag.find(
            'form', attrs={"method": "post", "action": "/signin"})
        input_once_tag = form_tag.find('input', attrs={"name": "once"})
        input_once_value = input_once_tag.attrs[1][1]
        
        input_username_tag = form_tag.find('input', attrs={"type" : "text", "placeholder" : "用户名或电子邮箱地址"})
	input_username_name = input_username_tag.attrs["name"]

	input_password_tag = form_tag.find('input', attrs={"type" : "password"})
	input_password_name = input_password_tag.attrs["name"]

	login_info = {
		"next": "/",
		input_username_name : self.username,
		input_password_name : self.password,
		"once": int(input_once_value),
		"next": "/"
	}

        # login
        self.v2ex_session.post(
            self.signin_url, data=login_info, headers=self.post_headers)
        main_req = self.v2ex_session.get(self.main_url, headers=self.headers)
        self.main_soup = BeautifulSoup.BeautifulSoup(main_req.content)
        top_tag = self.main_soup.find('div', attrs={"id": "Top"})
        user_tag = top_tag.find(href="/member/" + self.username)
        if not user_tag:
            print datetime.datetime.now(), " : v2ex signin failed for ", self.username
            return False
        else:
            return True

    def unchecked(self):
        award_tag = self.main_soup.find(href="/mission/daily")
        if award_tag:
            return True
        else:
            print datetime.datetime.now(), " : v2ex has already checked in ! \n"
            return False

    def checkin(self):
        # get award if haven't got it
        get_award_req = self.v2ex_session.get(
            self.award_url, headers=self.headers)
        get_award_soup = BeautifulSoup.BeautifulSoup(get_award_req.content)
        button_tag = get_award_soup.find('input', attrs={'type': 'button'})
        click_href = button_tag.attrs[3][1]
        first_dot_index = click_href.find("'")
        last_dot_index = click_href.find("'", first_dot_index + 1)
        click_url = self.main_url + click_href[
                                    first_dot_index + 1: last_dot_index]
        award_req = self.v2ex_session.get(click_url, headers=self.checkin_headers)
        if award_req.status_code == requests.codes.ok:
            print datetime.datetime.now(), " : v2ex checkin successfully ! \n"
        else:
            print datetime.datetime.now(), " : v2ex checkin failed with ", self.username, " ! \n"

    def run(self):
        if self.login():
            if self.unchecked():
                self.checkin()

