/**
 * LocalService.java
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

package de.rwth_aachen.awap;

public abstract class LocalService {
	protected Agent parent;
	protected int serviceId;
	public LocalService(Agent parent, int serviceId, ServiceDescription description) {
		this.parent = parent;
		this.serviceId = serviceId;
		this.parent.registerService(this, description);
	}

	public abstract boolean handleMessage(Message msg);

	public int getId() {
		return this.serviceId;
	}
}
