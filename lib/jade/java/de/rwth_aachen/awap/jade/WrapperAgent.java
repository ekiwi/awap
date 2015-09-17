package de.rwth_aachen.awap.jade;

import java.lang.reflect.Constructor;
import java.util.Date;
import java.util.TreeSet;

import de.rwth_aachen.awap.Agent;
import de.rwth_aachen.awap.jade.generated.Communication;
import de.rwth_aachen.awap.jade.node.Node;
import de.rwth_aachen.awap.jade.node.NodeAdapter;
import jade.core.behaviours.CyclicBehaviour;
import jade.core.behaviours.WakerBehaviour;
import jade.lang.acl.ACLMessage;

public class WrapperAgent extends jade.core.Agent {
	private static final long serialVersionUID = 1L;
	private Agent agent;
	private Node node;
	private NodeAdapter adapter;
	private TimeoutBehaviour timeoutBehaviour;

	public WrapperAgent(){
		timeoutBehaviour = new TimeoutBehaviour();
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
		this.addBehaviour(new ReceiveBehaviour());
		this.addBehaviour(timeoutBehaviour);

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
		//System.out.println(this.getName() + ":\n" + msg);
		try {
			MetaMessage rx = Communication.jadeToAwap(msg);
			// if this message was sent by a service, the service must be remote...
			if(rx.serviceTxMessage) {
				Communication.dispatchRemoteServiceMessage(this.agent, rx.msg);
			} else {
				this.agent.handleLocalServiceMessage(rx.msg);
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	public class ReceiveBehaviour extends CyclicBehaviour
	{
		private static final long serialVersionUID = 1L;
		public ReceiveBehaviour() {
			super(WrapperAgent.this);
		}

		@Override
		public void action() {
			ACLMessage msg = WrapperAgent.this.receive();
			if(msg != null) {
				WrapperAgent.this.handleMessage(msg);
			}
		}

	}

	protected void handleTimeout(Object data) {
		this.agent.onWakeUp(data);
	}

	public void addTimeout(int milliseconds, Object obj) {
		this.timeoutBehaviour.addTimeout(milliseconds, obj);
	}

	public class TimeoutBehaviour extends WakerBehaviour
	{
		class Timeout implements Comparable<Timeout>
		{
			public Date wakeup;
			public Object data;

			public Timeout(int milliseconds, Object data)
			{
				long timestamp = System.currentTimeMillis() + milliseconds;
				this.wakeup = new Date(timestamp);
				this.data = data;
			}

			@Override
			public int compareTo(Timeout other) {
				return this.wakeup.compareTo(other.wakeup);
			}

		}

		private static final long serialVersionUID = 1L;
		private TreeSet<Timeout> timeouts = new TreeSet<Timeout>();
		private Timeout activeTimeout = null;

		public TimeoutBehaviour() {
			super(WrapperAgent.this, 0);
			this.stop();
		}

		@Override
		protected void onWake() {
			if(activeTimeout != null) {
				WrapperAgent.this.handleTimeout(activeTimeout.data);
				timeouts.remove(activeTimeout);
			}
			reschedule();
		}

		public void addTimeout(int milliseconds, Object data) {
			Timeout tt = new Timeout(milliseconds, data);
			timeouts.add(tt);
			reschedule();
		}

		private void reschedule() {
			if(timeouts.size() > 0) {
				if(timeouts.first() != activeTimeout) {
					activeTimeout = timeouts.first();
					this.reset(activeTimeout.wakeup);
				}
			}
		}

	}
}
