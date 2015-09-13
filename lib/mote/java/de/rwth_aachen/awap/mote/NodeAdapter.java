package de.rwth_aachen.awap.mote;

import de.rwth_aachen.awap.Agent;
import de.rwth_aachen.awap.LocalService;
import de.rwth_aachen.awap.Message;
import de.rwth_aachen.awap.ServiceProperty;
import de.rwth_aachen.awap.node.AbstractNode;

public class NodeAdapter extends AbstractNode {
	public int agentId;

	public NodeAdapter(int agentId) {
		this.agentId = agentId;
	}

	public void send(Message msg) {
		Mote.send(agentId, msg);
	}

	public boolean deregisterService(LocalService service) {
		return Mote.deregisterService(agentId, service);
	}

	public byte installServiceListener(Agent listener, int serviceTypeId, ServiceProperty... properties) {
		return Mote.installServiceListener(serviceTypeId, listener, serviceTypeId, properties);
	}

	public boolean registerService(LocalService service) {
		return Mote.registerService(agentId, service);
	}

	public boolean uninstallServiceListener(byte listenerId) {
		return Mote.uninstallServiceListener(agentId, listenerId);
	}

}
