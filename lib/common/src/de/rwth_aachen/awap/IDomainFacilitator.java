package de.rwth_aachen.awap;

/**
 * Interface for a very minimal Domain Facilitator implementation.
 * Probably NOT FIPA compliant.
 * This interface assumes, that the local agent id is known.
 * Only services for the owning agent can be registered/deleted.
 * Only service listeners registered by the local agent can be
 * removed.
 *
 * @author Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 */
public interface IDomainFacilitator {
	/**
	 * Register a service with the Domain Facilitator
	 * @param serviceType service type constant
	 * @param properties  array of properties
	 * @return            node local id that identifies the service and
	 *                    can be used to later remove it
	 */
	// TODO: use correct type for properties
	public byte registerService(byte serviceType, byte[] properties);

	/**
	 * Remove a service, that was registered with the `registerService` method.
	 * @param serviceId id returned by the `registerService` method
	 * @return          `true` if remove was successful
	 */
	public boolean removeService(byte serviceId);

	/**
	 * Register a service listener with the Domain Facilitator
	 *
	 * The callback function will be called when a service, that fits the
	 * description, is found.
	 * @param listener    reference to an object that implements the callback
	 * @param serviceType
	 * @param properties
	 * @return
	 */
	public byte installServiceListener(IServiceListener listener,
			byte serviceType, byte[] properties);
}
