def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    selfT = set(tuple(map(int, p)) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(map(int, p)) for p in (observation.get("opponent_territory") or []))
    unclaimed = observation.get("unclaimed_cells") or []

    resources = observation.get("resources") or []
    rich = set()
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                rich.add((x, y))

    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_pos = observation.get("opponent_position", [None, None])
    ox, oy = (int(opp_pos[0]), int(opp_pos[1])) if opp_pos and opp_pos[0] is not None else (None, None)

    def nearest_dist(cell_set, x, y):
        best = 10**9
        if not cell_set:
            return best
        for (tx, ty) in cell_set:
            d = abs(tx - x) + abs(ty - y)
            if d < best:
                best = d
        return best

    target_cells = []
    for p in unclaimed:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                target_cells.append((x, y))
    if not target_cells:
        target_cells = list(oppT)

    target_set = set(target_cells)

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        val = 0
        if (nx, ny) in oppT:
            val += 120
            if ox is not None:
                val += max(0, 20 - (abs(nx - ox) + abs(ny - oy)))
        elif (nx, ny) in unclaimed:
            val += 55
        elif (nx, ny) not in selfT:
            val += 10

        if rich and (nx, ny) in rich:
            val += 140
        elif rich:
            val += max(0, 30 - nearest_dist(rich, nx, ny))

        if target_set:
            val += max(0, 40 - nearest_dist(target_set, nx, ny))

        if ox is not None:
            val += (abs(sx - ox) + abs(sy - oy)) - (abs(nx - ox) + abs(ny - oy))

        if val > best_val:
            best_val = val
            best_move = [int(dx), int(dy)]

    return best_move