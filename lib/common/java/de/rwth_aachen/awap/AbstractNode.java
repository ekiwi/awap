/**
 * AbstractNode.java
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

package de.rwth_aachen.awap;

public abstract class AbstractNode {
	public abstract void send(Message msg);
	public abstract void send(BroadcastMessage msg);

	/**
	 * Register a service with the "Domain Facilitator"
	 * @return        `true` if registration was successful
	 */
	public abstract boolean registerService(int localServiceId, ServiceDescription description);

	/**
	 * Deregister a service, that was registered with the `registerService` method.
	 * @param service service instance
	 * @return        `true` if remove was successful
	 */
	public abstract boolean deregisterService(int localServiceId);

	public abstract void requestWakeUp(int milliseconds, byte index);
}
