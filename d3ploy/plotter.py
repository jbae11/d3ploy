import matplotlib.pyplot as plt


def plot_demand_supply(all_dict, commod, test, demand_driven):
    """ Plots demand, supply, calculated demand and calculated supply on a curve 
    for a non-driving commodity 
    Parameters
    ----------
    4 dicts: dictionaries of supply, demand, calculated
    demand and calculated supply
    demand_driven: Boolean. If true, the commodity is demand driven, 
    if false, the commodity is supply driven 
    Returns
    -------
    plot of all four dicts 
    """
    
    dict_demand = all_dict['dict_demand']
    dict_supply = all_dict['dict_supply']
    dict_calc_demand = all_dict['dict_calc_demand']
    dict_calc_supply = all_dict['dict_calc_supply']

    fig, ax = plt.subplots(figsize=(15, 7))
    if demand_driven:
        ax.plot(*zip(*sorted(dict_demand.items())), '*', label='Demand')
        ax.plot(*zip(*sorted(dict_calc_demand.items())),
                'o', alpha=0.5, label='Calculated Demand')
        ax.set_title('%s Demand Supply plot' % commod)
    else:
        ax.plot(*zip(*sorted(dict_demand.items())), '*', label='Capacity')
        ax.plot(*zip(*sorted(dict_calc_demand.items())),
                'o', alpha=0.5, label='Calculated Capacity')
        ax.set_title('%s Capacity Supply plot' % commod)
    ax.plot(*zip(*sorted(dict_supply.items())), '*', label='Supply')
    ax.plot(*zip(*sorted(dict_calc_supply.items())),
            'o', alpha=0.5, label='Calculated Supply')
    ax.grid()
    ax.set_xlabel('Time (month timestep)', fontsize=14)
    ax.set_ylabel('Mass (kg)', fontsize=14)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        handles,
        labels,
        fontsize=11,
        loc='upper center',
        bbox_to_anchor=(
            1.1,
            1.0),
        fancybox=True)
    plt.savefig(test, dpi=300, bbox_inches='tight')
    plt.close()


def plot_supply_chain(cursor):
    """ plots the supply chain in the Cyclus simulation

    Parameters:
    -----------
    cursor: sqlite cursor
        cursor to the sqlite output file
    
    Returns:
    --------
    """
    protos = cursor.execute('SELECT DISTINCT(prototype) FROM agententry WHERE Kind = "Facility"').fetchall()
    chain_dict = {}
    sender_list = []
    receiver_list = []
    alpha = []
    omega = []
    for proto in protos:
        name = proto[0]
        query_str = """ SELECT DISTINCT(commodity) FROM transactions
                        INNER JOIN agententry 
                        ON agententry.agentid = transactions.senderid
                        WHERE prototype='%s'""" %name
        out_commod = query_result_to_list(cursor.execute(query_str).fetchall())
        in_commod = query_result_to_list(cursor.execute(query_str.replace('senderid', 'receiverid')).fetchall())
        
        # alpha and omega if they dont in or out any commodities
        if len(out_commod) == 0 and len(in_commod) != 0:
            omega.append(name)
        if len(in_commod) == 0 and len(out_commod) != 0:
            alpha.append(name)

        chain_dict[name] = {'in': in_commod,
                            'out': out_commod}
    print('chain dict', chain_dict)
    print('alpha', alpha)
    print('omega', omega)
    for a in alpha:
        for commodity in chain_dict[a]['out']:
            supply_chain = [a]
            commod_chain = [commodity]
            key = a
            while key not in omega:
                for key, val in chain_dict.items():
                    if commodity in val['in']:
                        supply_chain.append(key)
                        commod = chain_dict[key]['out']
                        if len(commod) == 0:
                            break
                        commod_chain.append(commod)
                        break
                print(commod_chain)
            string = ''
            print('commod chain', commod_chain)
            print('supply chain', supply_chain)

            for indx, val in enumerate(supply_chain):
                if val == supply_chain[-1]:
                    string += val
                    break
                string += val + '\t-----\t'
                try:
                    string += '[' + commod_chain[indx] + ']\t-----\t'
                except TypeError:
                    z = ''
                    for commod in commod_chain[indx]:
                        if commod != commod_chain[indx][-1]:
                            z += commod + ', '
                        else:
                            z += commod
                    string += '[' + z + ']\t-----\t'

    return string


def query_result_to_list(query_result, column_name=0):
    """ Converts sqlite query results to lists. The default value
        is integer 0, which is the first column in the query result."""
    x = []
    for result in query_result:
        x.append(result[column_name])
    return x

