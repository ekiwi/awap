package de.rwth_aachen.awap;

public abstract class Agent {
	private byte id;
	protected IDomainFacilitator df;

	public Agent(byte id, IDomainFacilitator df) {
		this.id = id;
		this.df = df;
	}

	protected byte getId() {
		return id;
	}

	/**
	 * This method is called when the agent is installed on a node.
	 */
	public abstract void setup();
	/**
	 * This method is called when the platform is about to shut down.
	 */
	public abstract void tearDown();
}
