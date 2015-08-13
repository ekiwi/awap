package de.rwth_aachen.awap.jade.node;

import jade.domain.DFService;
import jade.domain.FIPAException;
import jade.domain.FIPAAgentManagement.DFAgentDescription;
import jade.lang.acl.ACLMessage;

import java.util.ArrayList;
import java.util.HashMap;

import de.rwth_aachen.awap.Property;
import de.rwth_aachen.awap.RemoteAgent;
import de.rwth_aachen.awap.ServiceClient;
import de.rwth_aachen.awap.ServiceProvider;
import de.rwth_aachen.awap.TxMessage;
import de.rwth_aachen.awap.jade.AgentRegistry;
import de.rwth_aachen.awap.jade.WrapperAgent;
import de.rwth_aachen.awap.jade.generated.Communication;
import de.rwth_aachen.awap.jade.generated.Service;
import de.rwth_aachen.awap.node.AbstractNode;


/**
 * Presents a unique Node interface for every agent.
 * @author Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 * @author Artur Loewen <aloewen@eonerc.rwth-aachen.de>
 *
 */
public class NodeAdapter extends AbstractNode{

	private Node node;
	private WrapperAgent wrapper;
	// private LocalAgent agent;
	private ArrayList<ACLMessage> subscriptionMessages = new ArrayList<ACLMessage>();
	private HashMap<String, SubscriptionListener> subscriptionListeners = new HashMap<String, SubscriptionListener>();

	class SubscriptionListener {
		public byte listenerId;
		public ServiceClient listener;
		public SubscriptionListener(byte listenerId, ServiceClient listener) {
			this.listenerId = listenerId;
			this.listener = listener;
		}
	}

	public NodeAdapter(Node node, WrapperAgent wrapper){
		this.node = node;
		this.wrapper = wrapper;
	}

	@Override
	public void send(TxMessage tx_msg) {
		System.out.println("NodeAdapter: Agent " + this.wrapper.getName() + " called send.");
		ACLMessage msg = Communication.awapToJade(tx_msg);
		msg.setSender(this.wrapper.getAID());
		msg.addReceiver(AgentRegistry.getId(tx_msg.receiver.id));
		this.wrapper.send(msg);
	}

	@Override
	public boolean registerService(ServiceProvider service) {
		System.out.println("NodeAdapter: Agent " + this.wrapper.getName() + " called registerService.");

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
		System.out.println("NodeAdapter: Agent " + this.wrapper.getName() + " called deregisterService.");
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
			Property... properties) {
		System.out.println("NodeAdapter: Agent " + this.wrapper.getName() + " called installServiceListener.");

		// define search parameters
		DFAgentDescription dfd = new DFAgentDescription();
		try {
			dfd.addServices(Service.clientToDescription(listener, properties));
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			return -1;
		}

		ACLMessage subscriptionMessage =
				DFService.createSubscriptionMessage(this.wrapper, this.wrapper.getDefaultDF(), dfd, null);


		byte listenerId;
		synchronized(this.subscriptionMessages) {
			// save subscription message for later cancelation
			listenerId = (byte)this.subscriptionMessages.size();
			this.subscriptionMessages.add(subscriptionMessage);
		}

		this.subscriptionListeners.put(
				subscriptionMessage.getConversationId(),
				new SubscriptionListener(listenerId, listener));

		this.wrapper.send(subscriptionMessage);
		return listenerId;
	}

	/**
	 * Handles messages from the df.
	 * @return `true` if message was consumed
	 */
	public void handleDfMessage(ACLMessage msg) {
		try {
			SubscriptionListener sub = this.subscriptionListeners.get(msg.getConversationId());
			for(DFAgentDescription result : DFService.decodeNotification(msg.getContent())) {
				boolean registration = result.getAllServices().hasNext();
				RemoteAgent remoteAgent = new RemoteAgent();
				remoteAgent.id = AgentRegistry.getId(result.getName());
				if(registration) {
					System.out.println("NodeAdapter: Found new agent: " + result.getName());
					// TODO: call serviceFound with correct remote service
					// sub.listener.serviceFound(sub.listenerId, remoteAgent);
				} else {
					System.out.println("NodeAdapter: Agent died: " + result.getName());
					// TODO: call serviceRemoved with correct remote service
					// sub.listener.serviceRemoved(sub.listenerId, remoteAgent);
				}
			}
		} catch (FIPAException fe) {
			fe.printStackTrace();
		}
	}

	@Override
	public boolean uninstallServiceListener(byte listenerId) {
		System.out.println("NodeAdapter: Agent " + this.wrapper.getName() + " called uninstallServiceListener.");
		ACLMessage cancelMessage = DFService.createCancelMessage(
				this.wrapper, this.wrapper.getDefaultDF(), this.subscriptionMessages.get(listenerId));
		// send the message
		this.wrapper.send(cancelMessage);
		return true;
	}

}
