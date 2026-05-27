def solve_cvrp(instance):
    # ---------- helpers ----------
    def is_dict(x):
        return type(x) is dict

    def as_list(x):
        if type(x) in (list, tuple):
            return list(x)
        return None

    def get_capacity(inst):
        for k in ("capacity", "vehicle_capacity", "truck_capacity", "Q"):
            if k in inst:
                return inst[k]
        return None

    def get_depot_id(inst):
        if "depot_id" in inst:
            return inst["depot_id"]
        d = inst.get("depot", None)
        if is_dict(d) and "id" in d:
            return d["id"]
        return 0

    def get_depot_coord(inst):
        d = inst.get("depot", None)
        if is_dict(d):
            if "coord" in d:
                return d["coord"]
            if "coords" in d:
                return d["coords"]
            if "x" in d and "y" in d:
                return (d["x"], d["y"])
        if "depot_coord" in inst:
            return inst["depot_coord"]
        if "depot_coords" in inst:
            return inst["depot_coords"]
        return None

    def get_node_coord(node):
        if is_dict(node):
            if "coord" in node:
                return node["coord"]
            if "coords" in node:
                return node["coords"]
            if "x" in node and "y" in node:
                return (node["x"], node["y"])
        return None

    def get_node_demand(node):
        if is_dict(node):
            for k in ("demand", "dem", "q", "load"):
                if k in node:
                    return node[k]
        return None

    def parse_customers(inst):
        depot_id = get_depot_id(inst)
        coords = {}
        demands = {}
        ids = []

        # Common structured forms
        if "customers" in inst:
            c = inst["customers"]
            if is_dict(c):
                for cid, node in c.items():
                    if cid == depot_id:
                        continue
                    ids.append(cid)
                    dd = get_node_demand(node)
                    if dd is not None:
                        demands[cid] = dd
                    co = get_node_coord(node)
                    if co is not None:
                        coords[cid] = co
            else:
                arr = as_list(c)
                if arr is not None:
                    for idx, node in enumerate(arr):
                        cid = node["id"] if is_dict(node) and "id" in node else idx
                        if cid == depot_id:
                            continue
                        ids.append(cid)
                        dd = get_node_demand(node)
                        if dd is not None:
                            demands[cid] = dd
                        co = get_node_coord(node)
                        if co is not None:
                            coords[cid] = co

        elif "nodes" in inst:
            c = inst["nodes"]
            if is_dict(c):
                for cid, node in c.items():
                    if cid == depot_id:
                        continue
                    ids.append(cid)
                    dd = get_node_demand(node)
                    if dd is not None:
                        demands[cid] = dd
                    co = get_node_coord(node)
                    if co is not None:
                        coords[cid] = co
            else:
                arr = as_list(c)
                if arr is not None:
                    for idx, node in enumerate(arr):
                        cid = node["id"] if is_dict(node) and "id" in node else idx
                        if cid == depot_id:
                            continue
                        ids.append(cid)
                        dd = get_node_demand(node)
                        if dd is not None:
                            demands[cid] = dd
                        co = get_node_coord(node)
                        if co is not None:
                            coords[cid] = co

        else:
            # Flat mappings
            for key in ("demands", "demand", "q", "loads"):
                if key in inst:
                    d = inst[key]
                    if is_dict(d):
                        for cid, val in d.items():
                            if cid == depot_id:
                                continue
                            ids.append(cid)
                            demands[cid] = val
                    else:
                        arr = as_list(d)
                        if arr is not None:
                            for cid, val in enumerate(arr):
                                if cid == depot_id:
                                    continue
                                ids.append(cid)
                                demands[cid] = val

            for key in ("coords", "coordinates", "xy"):
                if key in inst:
                    c = inst[key]
                    if is_dict(c):
                        for cid, co in c.items():
                            if cid == depot_id:
                                continue
                            if cid not in ids:
                                ids.append(cid)
                            coords[cid] = co
                    else:
                        arr = as_list(c)
                        if arr is not None:
                            for cid, co in enumerate(arr):
                                if cid == depot_id:
                                    continue
                                if cid not in ids:
                                    ids.append(cid)
                                coords[cid] = co

        # Fallback: infer ids from matrix size if present
        if not ids:
            for key in ("distance_matrix", "dist_matrix", "cost_matrix"):
                if key in inst:
                    m = inst[key]
                    n = len(m)
                    for cid in range(n):
                        if cid != depot_id:
                            ids.append(cid)
                    break

        # Deduplicate and sort deterministically
        seen = {}
        out = []
        for cid in ids:
            if cid not in seen and cid != depot_id:
                seen[cid] = 1
                out.append(cid)
        try:
            out.sort()
        except:
            out = sorted(out, key=lambda x: str(x))
        return depot_id, out, demands, coords

    depot_id, customer_ids, demands, coords = parse_customers(instance)
    capacity = get_capacity(instance)
    if capacity is None:
        capacity = sum(demands.get(c, 0) for c in customer_ids)

    # ---------- distance ----------
    dist_matrix = None
    for key in ("distance_matrix", "dist_matrix", "cost_matrix"):
        if key in instance:
            dist_matrix = instance[key]
            break

    depot_coord = get_depot_coord(instance)

    def coord_of(cid):
        if cid == depot_id:
            return depot_coord
        return coords.get(cid, None)

    def dist(a, b):
        if dist_matrix is not None:
            try:
                return dist_matrix[a][b]
            except:
                pass
        ca = coord_of(a)
        cb = coord_of(b)
        if ca is not None and cb is not None:
            dx = ca[0] - cb[0]
            dy = ca[1] - cb[1]
            return (dx * dx + dy * dy) ** 0.5
        # Fallback deterministic pseudo-distance
        aa = a if type(a) in (int, float) else sum(ord(ch) for ch in str(a))
        bb = b if type(b) in (int, float) else sum(ord(ch) for ch in str(b))
        return abs(aa - bb) + 1.0

    def route_demand(route):
        s = 0
        for c in route:
            s += demands.get(c, 0)
        return s

    def route_cost(route):
        if not route:
            return 0
        c = dist(depot_id, route[0])
        for i in range(len(route) - 1):
            c += dist(route[i], route[i + 1])
        c += dist(route[-1], depot_id)
        return c

    # ---------- initial solution ----------
    routes = [[c] for c in customer_ids]

    # Clarke-Wright savings merge on route endpoints
    if len(customer_ids) >= 2:
        route_of = {c: i for i, c in enumerate(customer_ids)}
        active = {i: [customer_ids[i]] for i in range(len(customer_ids))}
        demand_of_route = {i: demands.get(customer_ids[i], 0) for i in range(len(customer_ids))}
        route_id_of_customer = {customer_ids[i]: i for i in range(len(customer_ids))}

        savings = []
        for i in range(len(customer_ids)):
            a = customer_ids[i]
            da = dist(depot_id, a)
            for j in range(i + 1, len(customer_ids)):
                b = customer_ids[j]
                s = da + dist(depot_id, b) - dist(a, b)
                savings.append((s, a, b))
        savings.sort(key=lambda x: (-x[0], str(x[1]), str(x[2])))

        def route_ends(r):
            if not r:
                return None, None
            return r[0], r[-1]

        for _, a, b in savings:
            ra = route_id_of_customer.get(a, None)
            rb = route_id_of_customer.get(b, None)
            if ra is None or rb is None or ra == rb:
                continue
            r1 = active.get(ra, None)
            r2 = active.get(rb, None)
            if not r1 or not r2:
                continue
            if demand_of_route[ra] + demand_of_route[rb] > capacity:
                continue

            a_first, a_last = route_ends(r1)
            b_first, b_last = route_ends(r2)

            merged = None
            if a_last == a and b_first == b:
                merged = r1 + r2
            elif a_first == a and b_last == b:
                merged = r2 + r1
            elif a_first == a and b_first == b:
                merged = list(reversed(r1)) + r2
            elif a_last == a and b_last == b:
                merged = r1 + list(reversed(r2))

            if merged is None:
                continue

            new_id = ra
            active[new_id] = merged
