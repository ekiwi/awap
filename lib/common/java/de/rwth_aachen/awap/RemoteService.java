/**
 * RemoteService.java
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

package de.rwth_aachen.awap;

public class RemoteService {
	protected Agent parent;
	public RemoteAgent remoteAgent;
	public int serviceId;

	public RemoteService(Agent parent, RemoteAgent remoteAgent, byte serviceId) {
		this.parent = parent;
		this.remoteAgent = remoteAgent;
		this.serviceId = serviceId;
	}
}
