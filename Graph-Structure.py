import networkx as nx
from faker import Faker
import matplotlib.pyplot as plt

fake = Faker()

G = nx.DiGraph()


def add_person():
    """
    Adds a new individual to the graph

    :return: The id of the new individual
    """

    person_id = fake.uuid4()
    person_data = {
        "name": fake.name(),
        "email": fake.email(),
        "address": fake.address(),
    }
    G.add_node(person_id, **person_data)
    return person_id


def add_random_connections(person_id, num_connections=3):
    """
    Adds random connections to the graph

    :param person_id: The id of the person to add connections to
    :param num_connections: The number of connections to add
    :return:
    """

    if len(G) > 1:
        possible_connections = [pid for pid in G.nodes if pid != person_id]
        for _ in range(min(num_connections, len(possible_connections))):
            target_id = fake.random_element(elements=possible_connections)
            connection_type = fake.random_element(elements=['friend', 'colleague', 'family', 'business_partner'])
            G.add_edge(person_id, target_id, relationship=connection_type)

            if fake.boolean(chance_of_getting_true=50):
                G.add_edge(target_id, person_id, relationship=connection_type)


if __name__ == "__main__":
    for _ in range(100):
        new_person_id = add_person()
        add_random_connections(new_person_id)

    plt.figure(figsize=(45, 30))

    print(G.nodes.data())
    print(G.edges.data())

    node_labels = nx.get_node_attributes(G, 'name')
    edge_labels = nx.get_edge_attributes(G,'relationship')

    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos, node_size=700)
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(data=True), edge_color='black')
    nx.draw_networkx_labels(G, pos, font_size=12, font_family='sans-serif', labels=node_labels)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.show()
