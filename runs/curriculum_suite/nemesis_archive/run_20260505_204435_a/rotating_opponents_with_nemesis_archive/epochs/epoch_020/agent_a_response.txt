def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal_xy(x, y):
        return inb(x, y) and (x, y) not in blocked

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    targets = []
    for r in resources:
        if isinstance(r, dict):
            pos = r.get("position", None)
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                targets.append((pos[0], pos[1]))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            targets.append((r[0], r[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not targets:
        # If no resources, move to reduce distance to opponent slightly (deterministic tie-break).
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal_xy(nx, ny):
                continue
            v = (man(nx, ny, ox, oy), dx, dy)
            if best is None or v < best[0]:
                best = (v, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Choose best target for each move: prioritize we can arrive first; else maximize lead pressure.
    best_move = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal_xy(nx, ny):
            continue

        # Evaluate best achievable target from this next position.
        best_for_move = None
        for tx, ty in targets:
            if not legal_xy(tx, ty):
                continue
            sd = man(nx, ny, tx, ty)
            od = man(ox, oy, tx, ty)
            # Primary: if we can reach at most as fast as opponent, reward that strongly.
            # Secondary: prefer smaller own distance.
            # Tertiary: if contesting, push where opponent is farther relative to us.
            contest_gap = od - sd
            v = (0 if sd <= od else 1, -contest_gap, sd, abs(tx - ox) + abs(ty - oy))
            if best_for_move is None or v < best_for_move:
                best_for_move = v

        # Also slightly discourage stepping adjacent to opponent (avoid easy captures in tight maps).
        adj = (abs(nx - ox) <= 1 and abs(ny - oy) <= 1)
        val = (best_for_move, 1 if adj else 0, man(nx, ny, ox, oy), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]] if best_move else [0, 0]