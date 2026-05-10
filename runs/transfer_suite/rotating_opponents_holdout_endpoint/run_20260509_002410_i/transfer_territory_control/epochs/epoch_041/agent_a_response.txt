def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    actions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def score_cell(x, y):
        if not inside(x, y) or (x, y) in obstacles:
            return -10**9
        # Prefer moving to cells adjacent to opponent territory (unclaimed) to initiate/accelerate flipping.
        adj_opp = False
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if inside(nx, ny) and (nx, ny) in opp_t:
                        adj_opp = True
                        break
            if adj_opp:
                break
        # Prefer unclaimed; allow stepping into opponent if it helps (flipping enabled).
        base = 0
        if (x, y) in unclaimed:
            base += 70
        if (x, y) in opp_t:
            base += 110  # flipping directly gains territory
        if (x, y) in self_t:
            base -= 5
        # Encourage frontier expansion: adjacent to our territory.
        adj_self = False
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if inside(nx, ny) and (nx, ny) in self_t:
                        adj_self = True
                        break
                if dx or dy:
                    pass
            if adj_self:
                break
        if adj_self:
            base += 25
        if adj_opp:
            base += 35
        # Distance shaping toward likely gain: closer to opponent frontier and nearer to center (reduce cornering).
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        base += int(6 - 0.5 * (abs(x - cx) + abs(y - cy)))
        if opp_t:
            mind = min(abs(x - ox) + abs(y - oy) for ox, oy in opp_t)
            base += int(20 - 1.0 * mind)
        return base

    # Deterministic tie-break: highest score, then smallest distance moved, then fixed action order by dx,dy.
    best_move = (0, 0)
    best = -10**18
    for dx, dy in actions:
        nx, ny = sx + dx, sy + dy
        sc = score_cell(nx, ny)
        moved = abs(dx) + abs(dy)
        key = (sc, -moved, -dx, -dy)  # deterministic
        if sc > best:
            best = sc
            best_move = (dx, dy)
        elif sc == best:
            cand_key = (sc, -moved, -dx, -dy)
            cur_key = (best, -(abs(best_move[0]) + abs(best_move[1])), -best_move[0], -best_move[1])
            if cand_key > cur_key:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]