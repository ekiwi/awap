/**
 * MetaMessage.java
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

package de.rwth_aachen.awap.jade;

import de.rwth_aachen.awap.Message;

/**
 * AwapMessage + Metadata
 * @author Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 */
public class MetaMessage {
	public Message msg;
	public boolean serviceTxMessage;

	public MetaMessage() {
		this.msg = null;
		this.serviceTxMessage = false;
	}

	public MetaMessage(Message msg, boolean serviceTxMessage) {
		this.msg = msg;
		this.serviceTxMessage = serviceTxMessage;
	}
}
