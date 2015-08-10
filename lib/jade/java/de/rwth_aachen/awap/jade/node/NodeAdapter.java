package de.rwth_aachen.awap.jade.node;

import jade.lang.acl.ACLMessage;
import de.rwth_aachen.awap.Property;
import de.rwth_aachen.awap.ServiceClient;
import de.rwth_aachen.awap.ServiceProvider;
import de.rwth_aachen.awap.TxMessage;
import de.rwth_aachen.awap.jade.WrapperAgent;
import de.rwth_aachen.awap.jade.generated.Communication;
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

	public NodeAdapter(Node node, WrapperAgent wrapper){
		this.node = node;
		this.wrapper = wrapper;
	}

	@Override
	public void send(TxMessage tx_msg) {
		ACLMessage msg = Communication.awapToJade(tx_msg);
		msg.setSender(this.wrapper.getAID());
		// TODO: determine receiver AID
	}

	@Override
	public boolean registerService(ServiceProvider service) {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public boolean deregisterService(ServiceProvider service) {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public byte installServiceListener(ServiceClient listener,
			byte serviceType, Property... properties) {
		// TODO Auto-generated method stub
		return 0;
	}

	@Override
	public boolean uninstallServiceListener(byte listenerId) {
		// TODO Auto-generated method stub
		return false;
	}

}
