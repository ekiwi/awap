package de.rwth_aachen.awap.jade;

import jade.core.Agent;

import java.lang.reflect.Constructor;

import de.rwth_aachen.awap.LocalAgent;
import de.rwth_aachen.awap.jade.node.Node;
import de.rwth_aachen.awap.jade.node.NodeAdapter;
import de.rwth_aachen.awap.node.AbstractNode;

public class WrapperAgent extends Agent {
	private static final long serialVersionUID = 1L;
	private LocalAgent agent;
	private Node node;
	private NodeAdapter adapter;

	public WrapperAgent(){
	}

	@Override
	protected void setup()
	{
		// retrieve arguments
		Object[] args = this.getArguments();
		assert args.length == 3;
		assert args[0] instanceof Node;
		assert args[1] instanceof String;
		assert args[2] instanceof Byte;

		this.node = (Node)args[0];
		String agent_class = (String)args[1];
		byte agentId = (Byte)args[2];

		this.adapter = new NodeAdapter(this.node, this);

		// create agent
		try {
			Class<?> c = Class.forName(agent_class);
			Constructor<?> ctor = c.getConstructor(byte.class, AbstractNode.class);
			this.agent = (LocalAgent)ctor.newInstance(agentId, this.adapter);
		} catch (Exception e) {
			e.printStackTrace();
		}

		// call setup
		super.setup();
		this.agent.setup();

		// debug
		System.out.println("New WrapperAgent for agent " + agentId +
				" on Node " + this.node.getName() + " of class `" + agent_class + "`!");
	}

	@Override
	protected void takeDown() {
		// deregister agent
		this.agent.tearDown();
		this.node.deregisterAgent(this.agent.getId());
		super.takeDown();
	}

}
