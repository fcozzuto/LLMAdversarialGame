def solve_cvrp(instance):
    def get_capacity(inst):
        for k in ("capacity", "vehicle_capacity", "max_load", "Q"):
            if isinstance(inst, dict) and k in inst:
                return inst[k]
        return 10 ** 18

    def is_num(x):
        return isinstance(x, (int, float))

    def node_xy(node):
        if isinstance(node, dict):
            if "x" in node and "y" in node and is_num(node["x"]) and is_num(node["y"]):
                return node["x"], node["y"]
        return None

    def get_depot(inst):
        if isinstance(inst, dict):
            for k in ("depot", "depot_id", "depot_index"):
                if k in inst:
                    d = inst[k]
                    if isinstance(d, dict):
                        return d
                    return {"id": d}
        return {"id": 0}

    def extract_customers(inst):
        depot = get_depot(inst)
        depot_id = depot.get("id", 0)
        customers = []
        if isinstance(inst, dict):
            for k in ("customers", "nodes", "points"):
                if k in inst and isinstance(inst[k], list):
                    for item in inst[k]:
                        if isinstance(item, dict):
                            cid = item.get("id", item.get("idx", item.get("node_id")))
                            if cid is None:
                                continue
                            if cid == depot_id:
                                continue
                            customers.append(item)
                    if customers:
                        break
        if not customers and isinstance(inst, dict):
            demands = inst.get("demands")
            coords = inst.get("coords") or inst.get("coordinates") or inst.get("positions")
            if isinstance(demands, dict):
                ids = list(demands.keys())
                for cid in ids:
                    if cid == depot_id:
                        continue
                    item = {"id": cid, "demand": demands[cid]}
                    if isinstance(coords, dict) and cid in coords:
                        xy = coords[cid]
                        if isinstance(xy, (list, tuple)) and len(xy) >= 2:
                            item["x"], item["y"] = xy[0], xy[1]
                    customers.append(item)
            elif isinstance(demands, list):
                for i, d in enumerate(demands):
                    cid = i
                    if cid == depot_id:
                        continue
                    item = {"id": cid, "demand": d}
                    if isinstance(coords, list) and i < len(coords):
                        xy = coords[i]
                        if isinstance(xy, (list, tuple)) and len(xy) >= 2:
                            item["x"], item["y"] = xy[0], xy[1]
                    customers.append(item)
        if not customers and isinstance(inst, dict):
            n = inst.get("n") or inst.get("num_customers") or inst.get("size")
            if isinstance(n, int):
                for cid in range(1, n + 1):
                    if cid == depot_id:
                        continue
                    customers.append({"id": cid, "demand": 1})
        return depot, customers

    def dist(a, b):
        if a is None or b is None:
            return 0
        ax = node_xy(a)
        bx = node_xy(b)
        if ax is None or bx is None:
            ai = a.get("id", 0) if isinstance(a, dict) else a
            bi = b.get("id", 0) if isinstance(b, dict) else b
            return abs(ai - bi)
        dx = ax[0] - bx[0]
        dy = ax[1] - bx[1]
        return (dx * dx + dy * dy) ** 0.5

    cap = get_capacity(instance)
    depot, custs = extract_customers(instance)
    depot_id = depot.get("id", 0)
    if "demand" not in depot:
        depot["demand"] = 0

    # Normalize customer records
    nodes = {depot_id: depot}
    for c in custs:
        cid = c.get("id", c.get("idx", c.get("node_id")))
        if cid is None:
            continue
        c = dict(c)
        c["id"] = cid
        c["demand"] = c.get("demand", 1)
        nodes[cid] = c

    customers = [nodes[cid] for cid in nodes if cid != depot_id]
    customers.sort(key=lambda x: (x.get("x", 0), x.get("y", 0), x["id"]))

    # If coordinates exist, use angle sweep ordering
    has_coords = True
    dx0 = depot.get("x", None)
    dy0 = depot.get("y", None)
    if dx0 is None or dy0 is None:
        has_coords = False
    else:
        for c in customers:
            if "x" not in c or "y" not in c:
                has_coords = False
                break
