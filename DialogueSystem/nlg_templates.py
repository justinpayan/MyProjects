#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

templates = {
    'say(text={text})':
        '{text}',


	'canthelp.uncovered_stop(from.street={street})':
		'I\'m sorry, but I do not have the schedule for buses serving {street} at this time. I only cover routes in the following areas: University of Georgia, and Normaltown.',

	'open-request()':
		'Open request. I still do not know what this means.',

	'are-you-there()':
	(
		'Are you still there?',
		'I\'m sorry, I didn\'t quite catch that. Please repeat yourself',
		'What was that again?',
	),

	'please-repeat()':
		'I didn\'t quite catch that. Please repeat yourself.',

	'hold-on()':
		'Please hold on.',

	'canthelp.uncovered_route({route_name})':
		'Route {route_name} is not in this system',

	'canthelp.from_equals_to()':
		'Can\'t help. From equals to.',

	'expl-conf(slot={slot})&expl-conf(val={val})':
		'You want your {slot} to be {val}, is that right?',

	'please-rephrase()':
		'I didn\'t understand the content of your statement. Please rephrase it.',

	'example(act=restart)':
		'For example, you can say start over to restart.',

	'example(time.rel=next)':
		'For example, you can say I want the next bus.',
	
	'impl-conf()':
		'Ok, sure. Please give me more information about your desired route.',

	'bebrief()':
		'I\'m sorry, this conversation is taking too long',

	'schedule()':
		'There is a bus from such and such place',

	'canthelp.cant_find_stop(stop={stop})':
		'I\'m sorry, I can\'t find the stop {stop}',

	'noAction()':
		'We are finished. Goodbye.',

	'restart()':
		'I understand you\'d like to restart. Here we go!',

	'canthelp.system_error()':
		'I\'m sorry, there was a massive error. Please exit immediately',

	'ack()':
		'Great, please give me more information about the route.',

	'request(from.neighborhood)':
		'What neighborhood do you want to leave from?',
	'request(from.street)':
		'What street do you want to leave from?',
	'request(from.poi)':
		'What monument do you want to leave from?',
	'request(to.neighborhood)':
		'What neighborhood do you want to go to?',
	'request(to.street)':
		'What street do you want to go to?',
	'request(to.poi)':
		'What monument do you want to go to?',
	'request(route)':
		'What route do you want to take?',
	'request(date.day)':
		'What neighborhood do you want to go to?',
	'request(time.minute)':
		'What is the minute value of the time you wish to travel?',
	'request(time.hour)':
		'What hour do you wish to travel at?',
	'request(time.rel)':
		'What is the relative time you want to leave? For instance, you can say tomorrow or today.',
	'request(time.ampm)':
		'Is the time a.m. or p.m.?',

	'canthelp.route_doesnt_run(route={route})':
		'The route {route} doesn\'t run anymore',

	'canthelp.no_buses_at_time(hour={hour})&canthelp.no_buses_at_time(minute={minute})&canthelp.no_buses_at_time(ampm={ampm})':
		'Sorry, there aren\'t any buses at the time {hour} {minute} {ampm}.',

	'hello2()':	
        (
            'I will help you find information about local bus routes, given the details you have provided.',
	    'How may I help you find bus route information today?'
        ),

	'hello1()':	
        (
            'Hello, this is Usman and Justin\'s dialogue system. I help you find information about local bus routes. How may I help you?',
	    'Hi, how may I help you find bus route information today?'
        ),

	'canthelp.no_connection()':
		'Can\'t help, no connection.'
}
