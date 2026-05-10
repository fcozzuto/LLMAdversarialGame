def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = list(observation.get("unclaimed_cells") or [])
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    dirs9 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    t = int(observation.get("turn_index", 0))
    dirs = dirs9[t % 9:] + dirs9[:t % 9]

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    nbrs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    def near_opp(cell):
        cx, cy = cell
        for dx, dy in nbrs:
            if (cx + dx, cy + dy) in opp_terr:
                return 1
        return 0

    # Prefer unclaimed cells, weighted to capture near opponent territory while staying close.
    if unclaimed:
        cand = unclaimed
    else:
        # Fallback: try to invade adjacent to opponent territory.
        cand = []
        for x, y in opp_terr:
            for dx, dy in nbrs:
                nx, ny = x + dx, y + dy
                if inside(nx, ny) and (nx, ny) not in obstacles and (nx, ny) not in self_terr and (nx, ny) not in opp_terr:
                    cand.append([nx, ny])
        # Last fallback: expand to any unoccupied near us (from grid-unclaimed not available).
        if not cand:
            cand = [[sx + dx, sy + dy] for dx, dy in nbrs if inside(sx + dx, sy + dy) and (sx + dx, sy + dy) not in obstacles]

    target = None
    best = None
    for p in cand:
        x, y = p
        if not inside(x, y) or (x, y) in obstacles:
            continue
        # Deterministic tie-breaks by coordinates.
        score = (man(sx, sy, x, y) - 2.2 * near_opp((x, y))) + 0.03 * man(ox, oy, x, y)
        tb = (score, x, y)
        if best is None or tb < best:
            best = tb
            target = (x, y)

    # Choose legal step that most improves distance to target, with deterministic order.
    if target is None:
        return [0, 0]
    tx, ty = target

    best_move = (0, 0); best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        # Move preference: closer to target; slight preference to not step into opponent territory too early unless it is beneficial.
        val = man(nx, ny, tx, ty)
        # Encourage stepping on opponent/into contested to flip (if enabled) when adjacent.
        if (nx, ny) in opp_terr:
            val -= 0.6
        if best_val is None or (val, nx, ny) < (best_val, best_move[0] + sx, best_move[1] + sy):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]