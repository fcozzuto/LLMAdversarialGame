def choose_move(observation):
    w, h = observation.get("grid_width", 0), observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obs = set(observation.get("obstacles") or [])
    un = list(observation.get("unclaimed_cells") or [])
    resources = list(observation.get("resources") or [])
    turn = observation.get("turn_index", 0)
    behind = False
    myc = observation.get("self_territory_count", 0)
    opc = observation.get("opponent_territory_count", 0)
    if myc < opc:
        behind = True
    attack = (turn % 2 == 1) or not behind

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in neigh + [(0, 0)]:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            cand.append((dx, dy))
    if not cand:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = un if un else (resources if resources else [])
    if attack or not targets:
        targets = [((ox, oy))]
    else:
        if not targets:
            targets = [((ox, oy))]

    best = None
    bestv = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        d = min(man((nx, ny), t) for t in targets) if targets else 0
        # Prefer moving onto unclaimed/resources deterministically, then closer to target.
        bonus = 0
        if (nx, ny) in obs:
            bonus = -10**9
        elif (nx, ny) in set(un):
            bonus += 50
        elif (nx, ny) in set(resources):
            bonus += 20
        # Slight bias toward opponent when attacking, toward center otherwise.
        bias = man((nx, ny), (w // 2, h // 2))
        if attack:
            bias = -man((nx, ny), (ox, oy))
        v = bonus - d + (0.001 * (-bias))
        if bestv is None or v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]