/**
 * BroadcastMessage.java
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

package de.rwth_aachen.awap;

public class BroadcastMessage {
	public Message msg;
	public ServiceDescription recipients;
	public BroadcastMessage(Message msg, ServiceDescription recipients) {
		this.msg = msg;
		this.recipients = recipients;
	}
}
