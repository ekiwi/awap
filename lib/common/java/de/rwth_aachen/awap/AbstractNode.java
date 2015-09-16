package de.rwth_aachen.awap;

public abstract class AbstractNode {
	public abstract void send(Message msg);

	/**
	 * Register a service with the "Domain Facilitator"
	 * @param service service instance
	 * @return        `true` if registration was successful
	 */
	public abstract boolean registerService(LocalService service);

	/**
	 * Deregister a service, that was registered with the `registerService` method.
	 * @param service service instance
	 * @return        `true` if remove was successful
	 */
	public abstract boolean deregisterService(LocalService service);

	public abstract void requestWakeUp(int milliseconds, Object obj);
}
