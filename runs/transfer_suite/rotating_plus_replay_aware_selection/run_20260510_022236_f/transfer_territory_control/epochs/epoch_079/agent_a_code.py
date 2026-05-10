def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)]
    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    sc = observation.get("scores") or {}
    my_score = sc.get("self", sc.get("me", 0)) if isinstance(sc, dict) else 0
    op_score = sc.get("opponent", sc.get("op", 0)) if isinstance(sc, dict) else 0
    if my_score == 0 and op_score == 0:
        upc = int(observation.get("self_territory_count") or 0)
        opc = int(observation.get("opponent_territory_count") or 0)
        my_score, op_score = upc, opc
    behind = my_score < op_score

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_op(x, y):
        return ((x + 1, y) in op_terr) or ((x - 1, y) in op_terr) or ((x, y + 1) in op_terr) or ((x, y - 1) in op_terr)

    best = None
    bestv = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        v = 0
        if (nx, ny) in op_terr:
            v -= 100000
        if (nx, ny) in unclaimed:
            v += 10000 if not behind else 12000
        if (nx, ny) in self_terr:
            v += 1000
        if adj_op(nx, ny):
            v += 5000 if not behind else 6500
        if behind and (nx, ny) not in self_terr:
            v += 200
        if (nx, ny) in unclaimed and (nx, ny) not in self_terr:
            v += 50
        if v > bestv:
            bestv = v
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best