package de.rwth_aachen.awap.mote;

import de.rwth_aachen.awap.BroadcastMessage;
import de.rwth_aachen.awap.LocalService;
import de.rwth_aachen.awap.Message;
import de.rwth_aachen.awap.AbstractNode;

public class NodeAdapter extends AbstractNode {
	public int agentId;

	public NodeAdapter(int agentId) {
		this.agentId = agentId;
	}

	public native void send(Message msg);
	public native void send(BroadcastMessage msg);
	public native void requestWakeUp(int milliseconds, Object obj);
	public native boolean deregisterService(LocalService service);
	public native boolean registerService(LocalService service);
}
