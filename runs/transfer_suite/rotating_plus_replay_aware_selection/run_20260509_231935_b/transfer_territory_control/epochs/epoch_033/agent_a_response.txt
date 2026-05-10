def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    sx, sy = int(sx), int(sy)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]
    if observation.get("environment_name") != "territory_control":
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose a deterministic target: prefer unclaimed; else attack opponent territory; else head to opponent.
    if unclaimed:
        tx, ty = min(unclaimed, key=lambda p: (md(sx, sy, p[0], p[1]), p[0], p[1]))
    elif opp_terr:
        tx, ty = min(opp_terr, key=lambda p: (md(sx, sy, p[0], p[1]), p[0], p[1]))
    else:
        tx, ty = map(int, observation["opponent_position"])

    # Prefer moves that claim/flip and make progress.
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    t = int(observation.get("turn_index", 0))
    r = t % 9
    dirs = dirs[r:] + dirs[:r]

    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            v = -10**12
        else:
            if (nx, ny) in self_terr:
                claim = 2
            elif (nx, ny) in opp_terr:
                claim = 14  # flipping
            else:
                claim = 7 if (nx, ny) in set(unclaimed) else 4
            # Progress + light anti-stall: keep moving toward target and slightly away from obstacles
            v = claim * 1000 - md(nx, ny, tx, ty) * 25
            # If adjacent to obstacle, prefer moves that don't push into it next
            adj_obs = 0
            for ex in (-1, 0, 1):
                for ey in (-1, 0, 1):
                    if ex == 0 and ey == 0:
                        continue
                    xx, yy = nx + ex, ny + ey
                    if inb(xx, yy) and (xx, yy) in obstacles:
                        adj_obs += 1
            v -= adj_obs * 3
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])] if best is not None else [0, 0]