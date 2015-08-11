package de.rwth_aachen.awap.node;

import de.rwth_aachen.awap.Property;
import de.rwth_aachen.awap.ServiceClient;
import de.rwth_aachen.awap.ServiceProvider;

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
	 * @param service service instance
	 * @return        `true` if registration was successful
	 */
	public boolean registerService(ServiceProvider service);

	/**
	 * Deregister a service, that was registered with the `registerService` method.
	 * @param service service instance
	 * @return        `true` if remove was successful
	 */
	public boolean deregisterService(ServiceProvider service);

	/**
	 * Register a service listener with the Domain Facilitator
	 *
	 * The callback function will be called when a service, that fits the
	 * description, is found.
	 * Fitting services, that are already known to the DF will trigger e.. vs []vents
	 * just like the insertion or removal of a fitting service.
	 * @param listener    reference to an object that implements the callback
	 * @param properties  array of properties that need to match
	 * @return            node local id that identifies the service listener
	 *                    and can be used to later remove it
	 */
	public byte installServiceListener(ServiceClient listener,
			Property... properties);
	/**
	 * Unregisters a service listener that was installed with the
	 * `installServiceListener` method
	 * @param listenerId id returned by the `installServiceListener` method
	 * @return           `true` if uninstall was successful
	 */
	// TODO: should this trigger a service removed event to be handed to the listener?
	public boolean uninstallServiceListener(byte listenerId);
}