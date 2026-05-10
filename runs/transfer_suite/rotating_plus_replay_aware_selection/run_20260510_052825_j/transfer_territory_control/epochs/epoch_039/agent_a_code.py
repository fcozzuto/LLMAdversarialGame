def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    neigh4 = [(-1,0),(1,0),(0,-1),(0,1)]
    def adj_to(sset, cx, cy):
        for dx, dy in neigh4:
            tx, ty = cx + dx, cy + dy
            if inb(tx, ty) and (tx, ty) in sset:
                return True
        return False

    def cell_score(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        s = 0
        if (nx, ny) in oppT:
            s += 30
            s += 5 if adj_to(selfT, nx, ny) else 0
            s += 3 if adj_to(oppT, nx, ny) else 0
        elif (nx, ny) in unclaimed:
            s += 18
            s += 6 if adj_to(selfT, nx, ny) else 0
            s += 4 if adj_to(oppT, nx, ny) else 0
        elif (nx, ny) in selfT:
            s += 8
            s += 3 if adj_to(selfT, nx, ny) else 0
        else:
            s += 0

        # Drive into opponent frontier: prefer reducing distance to opponent and to opponent-adjacent unclaimed
        s -= (abs(nx - ox) + abs(ny - oy)) * 0.5
        if unclaimed:
            best = None
            for dx, dy in neigh4:
                tx, ty = nx + dx, ny + dy
                if inb(tx, ty) and (tx, ty) in unclaimed:
                    d = abs(tx - ox) + abs(ty - oy)
                    if best is None or d < best:
                        best = d
            if best is not None:
                s += 2.0

        return s

    best_move = (0, 0)
    best_val = -10**18
    # deterministic tie-break: iterate dirs in fixed order, keep first with max score
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        v = cell_score(nx, ny)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]