def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    resources = observation.get("resources") or []

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def adj_opp(x, y):
        c = 0
        for dx, dy in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in opp_terr:
                c += 1
        return c

    if resources:
        tx, ty = resources[0]
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = abs(tx - nx) + abs(ty - ny)
            if best is None or d < best[0]:
                best = (d, [dx, dy])
        if best is not None:
            return best[1]

    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        dist_center = abs(nx - cx) + abs(ny - cy)
        in_opp = (nx, ny) in opp_terr
        in_self = (nx, ny) in self_terr
        in_un = (nx, ny) in unclaimed

        # Prefer center control, reward invading opponent, and cutting via contested adjacency.
        val = dist_center
        val += -3.0 if in_opp else 0.0
        val += -0.2 if in_self else 0.0
        val += -0.1 if in_un else 0.0
        val += -0.7 * adj_opp(nx, ny)

        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move