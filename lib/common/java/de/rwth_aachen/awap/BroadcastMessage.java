package de.rwth_aachen.awap;

public class BroadcastMessage {
	public Message msg;
	public ServiceFilter recipients;
	public BroadcastMessage(Message msg, ServiceFilter recipients) {
		this.msg = msg;
		this.recipients = recipients;
	}
}
