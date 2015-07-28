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
	 * Deregister a service, that was registered with the `registerService` method.
	 * @param serviceId id returned by the `registerService` method
	 * @return          `true` if remove was successful
	 */
	public boolean deregisterService(byte serviceId);

	/**
	 * Register a service listener with the Domain Facilitator
	 *
	 * The callback function will be called when a service, that fits the
	 * description, is found.
	 * Fitting services, that are already known to the DF will trigger events
	 * just like the insertion or removal of a fitting service.
	 * @param listener    reference to an object that implements the callback
	 * @param serviceType service type constant
	 * @param properties  array of properties that need to match
	 * @return            node local id that identifies the service listener
	 *                    and can be used to later remove it
	 */
	public byte installServiceListener(IServiceListener listener,
			byte serviceType, byte[] properties);

	/**
	 * Unregisters a service listener that was installed with the
	 * `installServiceListener` method
	 * @param listenerId id returned by the `installServiceListener` method
	 * @return           `true` if uninstall was successful
	 */
	// TODO: should this trigger a service removed event to be handed to the listener?
	public boolean uninstallServiceListener(byte listenerId);
}