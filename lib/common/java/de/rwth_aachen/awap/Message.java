/**
 * Message.java
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

package de.rwth_aachen.awap;

public class Message {
	private int remoteAgentId;
	public int serviceTypeId;
	public RemoteAgent getRemoteAgent() {
		return new RemoteAgent(remoteAgentId);
	}
	public void setRemoteAgent(RemoteAgent agent) {
		this.remoteAgentId = agent.id;
	}
}
