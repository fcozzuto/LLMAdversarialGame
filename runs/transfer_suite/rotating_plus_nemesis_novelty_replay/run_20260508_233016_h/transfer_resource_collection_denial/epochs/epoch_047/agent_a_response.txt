def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Estimate sweep_rows threat: prefer resources not on/near opponent's row.
    opp_row = oy
    row_pen = 0
    # row_pen will be applied per resource based on distance in y.
    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Choose target under a greedy "win-first" heuristic from this hypothetical position.
        chosen = None
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            # Big reward for being closer; penalize if opponent is closer.
            base = (opd - myd) * 10
            # Row sweep avoidance: opponent sweeping its current row likely soon.
            ry_dist = abs(ry - opp_row)
            sweep_avoid = - (4 - min(4, ry_dist)) * 3  # highest penalty when ry matches opponent row
            # Slight tie-break: prefer shorter myd.
            tie = -myd
            val = base + sweep_avoid + tie
            if chosen is None or val > chosen[0]:
                chosen = (val, rx, ry)

        if chosen is None:
            val = -10**9
        else:
            val, tx, ty = chosen
            # Add micro-lookahead: next step should keep reducing distance to target and not drift into obstacles.
            myd_now = man(nx, ny, tx, ty)
            # If we are already at the target, strongly prefer.
            val += 50 if myd_now == 0 else -myd_now

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]