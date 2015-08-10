package de.rwth_aachen.awap.jade.node;

import jade.domain.DFService;
import jade.domain.FIPAException;
import jade.domain.FIPAAgentManagement.DFAgentDescription;
import jade.lang.acl.ACLMessage;
import jade.proto.SubscriptionInitiator;

import java.util.ArrayList;

import de.rwth_aachen.awap.Property;
import de.rwth_aachen.awap.ServiceClient;
import de.rwth_aachen.awap.ServiceProvider;
import de.rwth_aachen.awap.TxMessage;
import de.rwth_aachen.awap.jade.WrapperAgent;
import de.rwth_aachen.awap.jade.generated.Communication;
import de.rwth_aachen.awap.jade.generated.Service;
import de.rwth_aachen.awap.node.AbstractNode;


/**
 * Presents a unique Node interface for every agent.
 * @author Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 */
public class NodeAdapter extends AbstractNode{

	private Node node;
	private WrapperAgent wrapper;
	// private LocalAgent agent;
	private ArrayList<ACLMessage> subscriptionMessages = new ArrayList<ACLMessage>();

	public NodeAdapter(Node node, WrapperAgent wrapper){
		this.node = node;
		this.wrapper = wrapper;
	}

	@Override
	public void send(TxMessage tx_msg) {
		ACLMessage msg = Communication.awapToJade(tx_msg);
		msg.setSender(this.wrapper.getAID());
		System.out.println("Agent " + this.wrapper.getName() + " called send.");
	}

	@Override
	public boolean registerService(ServiceProvider service) {
		System.out.println("Agent " + this.wrapper.getName() + " called registerService.");

		DFAgentDescription dfd = new DFAgentDescription();
		dfd.setName(this.wrapper.getAID());
		try {
			dfd.addServices(Service.providerToDescription(service));
		} catch(Exception e) {
			e.printStackTrace();
			return false;
		}

		try {
			DFService.register(this.wrapper, dfd);
			return true;
		} catch (FIPAException fe) {
			fe.printStackTrace();
			return false;
		}
	}

	@Override
	public boolean deregisterService(ServiceProvider service) {
		System.out.println("Agent " + this.wrapper.getName() + " called deregisterService.");
		try {
			DFService.deregister(this.wrapper);
			return true;
		} catch (FIPAException fe) {
			fe.printStackTrace();
			return false;
		}
	}

	@Override
	public byte installServiceListener(ServiceClient listener,
			byte serviceType, Property... properties) {
		System.out.println("Agent " + this.wrapper.getName() + " called installServiceListener.");

		// define search parameters
		DFAgentDescription dfd = new DFAgentDescription();
		try {
			dfd.addServices(Service.clientToDescription(listener, properties));
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			return -1;
		}

		// create the subscription message using the created description
		ACLMessage subscriptionMessage =
				DFService.createSubscriptionMessage(this.wrapper, this.wrapper.getDefaultDF(), dfd, null);

		// create and add the notification behavior
		this.wrapper.addBehaviour(new SubscriptionInitiator(this.wrapper, subscriptionMessage)
		{
			private static final long serialVersionUID = 1L;

			// this method handles incoming INFORM messages sent by the directory service
			// whenever an agent of the given type with fitting properties is registered/deregistered
			protected void handleInform(ACLMessage inform)
			{
				try
				{
					// decode message content
					DFAgentDescription[] result = DFService.decodeNotification(inform.getContent());

					// process agent description entries
					for (int i = 0; i < result.length; ++i)
					{
						// TODO: notify agent!
						System.out.println(result);
					}
				}
				catch (FIPAException fe)
				{
					fe.printStackTrace();
				}
			}
		});

		// save subscription message for later cancelation
		this.subscriptionMessages.add(subscriptionMessage);
		return (byte)(this.subscriptionMessages.size() - 1);
	}

	@Override
	public boolean uninstallServiceListener(byte listenerId) {
		System.out.println("Agent " + this.wrapper.getName() + " called uninstallServiceListener.");
		return false;
	}

}
