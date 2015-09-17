package de.rwth_aachen.awap.jade;

import java.lang.reflect.Constructor;

import de.rwth_aachen.awap.Agent;
import de.rwth_aachen.awap.Message;
import de.rwth_aachen.awap.jade.generated.Communication;
import de.rwth_aachen.awap.jade.node.Node;
import de.rwth_aachen.awap.jade.node.NodeAdapter;
import jade.core.behaviours.CyclicBehaviour;
import jade.lang.acl.ACLMessage;

public class WrapperAgent extends jade.core.Agent {
	private static final long serialVersionUID = 1L;
	private Agent agent;
	private Node node;
	private NodeAdapter adapter;

	public WrapperAgent(){
	}

	public Agent getAwapAgent() {
		return this.agent;
	}
	@Override
	protected void setup()
	{
		// retrieve arguments
		Object[] args = this.getArguments();
		assert args.length == 3;
		assert args[0] instanceof Node;		// the node this is running on
		assert args[1] instanceof String;	// full name of the awap agent class
		assert args[2] instanceof Byte;		// the local id of the agent

		this.node = (Node)args[0];
		String agent_class = (String)args[1];
		byte agentId = (Byte)args[2];

		this.adapter = new NodeAdapter(this.node, this);

		// create agent
		try {
			Class<?> c = Class.forName(agent_class);
			Constructor<?> ctor = c.getConstructor();
			this.agent = (Agent)ctor.newInstance();
			this.agent.init(agentId, this.adapter);
		} catch (Exception e) {
			e.printStackTrace();
		}

		// call setup
		super.setup();
		this.agent.setup();

		// add receive behavior
		this.addBehaviour(new ReceiveBehaviour(this));

		// debug
		//System.out.println("New WrapperAgent for agent " + agentId +
		//		" on Node " + this.node.getName() + " of class `" + agent_class + "`!");
	}

	@Override
	protected void takeDown() {
		// deregister agent
		this.agent.tearDown();
		this.node.deregisterAgent(this.agent.getId());
		super.takeDown();
	}

	protected void handleMessage(ACLMessage msg){
		if(msg.getSender().equals(this.getDefaultDF())) {
			this.adapter.handleDfMessage(msg);
		} else {
			//System.out.println(this.getName() + ":\n" + msg);
			Message rx;
			try {
				rx = Communication.jadeToAwap(msg);

				if(rx.remoteService) {
					Communication.dispatchRemoteServiceMessage(this.agent, rx);
				} else {
					this.agent.handleLocalServiceMessage(rx);
				}
			} catch (Exception e) {
				e.printStackTrace();
			}
		}
	}

	public class ReceiveBehaviour extends CyclicBehaviour
	{
		private static final long serialVersionUID = 1L;
		private WrapperAgent parent;
		public ReceiveBehaviour(WrapperAgent agent) {
			super(agent);
			this.parent = agent;
		}

		@Override
		public void action() {
			ACLMessage msg = this.parent.receive();
			if(msg != null) {
				this.parent.handleMessage(msg);
			}
		}

	}

}
