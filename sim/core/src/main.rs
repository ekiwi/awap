#[derive(Debug)]
struct Packet {
	src: u32,
	dest: u32,
	data: [u8; 10],
}


enum NodeCommand {
	WaitForPacket,
	GoToSleep(u64, u64),
}

struct Node {
	name: String,
	address: u32,
}


impl Node {
	/// node will stay awake untill it receives it's first packet
	fn init(&self) -> NodeCommand {
		NodeCommand::WaitForPacket
	}

	fn receive_packet(&self, packet: &Packet) -> NodeCommand {
		println!("{} received a packet: {:?}", self.name, packet);
		NodeCommand::WaitForPacket
	}
}

struct SimulatedNode {
	node: Node,
	ticks_awake: u64,
	ticks_asleep: u64,
	sleeping: bool,
	command: NodeCommand,
}

fn main() {
	// setup simulation
	let mut node0 = Node{ name: "Node0".to_string(), address: 1};
	let mut node0sim = SimulatedNode {
		command: node0.init(),
		node: node0,
		ticks_awake: 0,
		ticks_asleep: 0,
		sleeping: false
	};
	let mut nodes = vec![node0sim];

	let mut packets = Vec::new();
	packets.push(Packet { src: 0, dest:1, data: [0; 10]});

	// run simulator
	let max_tick = 100u64;

	for tick in 0..max_tick {
		// distribute packets
		match packets.pop() {
			Some(packet) => {
				for node in nodes.iter_mut() {
					if !node.sleeping  && node.node.address != packet.src {
						node.command = node.node.receive_packet(&packet);
					}
				}
			},
			None => ()
		};

		// update nodes
		for node in nodes.iter_mut() {
			if node.sleeping {
				node.ticks_asleep += 1;
			} else {
				node.ticks_awake += 1;
			}

			node.command = match node.command {
				NodeCommand::WaitForPacket => NodeCommand::WaitForPacket,
				NodeCommand::GoToSleep(0,0) => NodeCommand::GoToSleep(0,0),
				NodeCommand::GoToSleep(0,ticks) => NodeCommand::GoToSleep(0,ticks-1),
				NodeCommand::GoToSleep(ticks,n) => NodeCommand::GoToSleep(ticks-1,n)
			};

			node.sleeping = match node.command {
				NodeCommand::WaitForPacket => false,
				NodeCommand::GoToSleep(0,0) => false,
				NodeCommand::GoToSleep(0,ticks) => true,
				NodeCommand::GoToSleep(_,_) => false
			};
		}
	}
}
