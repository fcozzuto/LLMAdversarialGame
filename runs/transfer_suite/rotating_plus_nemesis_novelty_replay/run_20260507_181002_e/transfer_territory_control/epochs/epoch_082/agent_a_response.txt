def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = set(resources)

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Candidate targets: unclaimed first, else opponent cells
    candidates = list(unclaimed) if unclaimed else list(oppT)
    if not candidates:
        return [0, 0]

    # Deterministic: sort by (distance to self, farther from opponent, edge preference, coords)
    def edge_pref(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    candidates.sort(key=lambda t: (man(sx, sy, t[0], t[1]), -man(ox, oy, t[0], t[1]), edge_pref(t[0], t[1]), t[0], t[1]))

    # Take a small deterministic shortlist and pick best by combined heuristic
    shortlist = candidates[:max(1, min(10, len(candidates)))]
    best_target = None
    best_tval = None
    for tx, ty in shortlist:
        if (tx, ty) in obstacles:
            continue
        tval = 3 * man(sx, sy, tx, ty) - man(ox, oy, tx, ty) - 0.2 * edge_pref(tx, ty)
        if best_tval is None or tval < best_tval:
            best_tval = tval
            best_target = (tx, ty)
    if best_target is None:
        return [0, 0]
    tx, ty = best_target

    # Choose best immediate move (including stay), avoid stepping into obstacles
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        capture = 0
        if cell in unclaimed:
            capture += 8
        elif cell in oppT:
            capture += 6
        elif cell in selfT:
            capture += 2

        prog = -man(nx, ny, tx, ty)
        avoid_opp = -0.25 * man(nx, ny, ox, oy)
        center = -0.02 * (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))

        val = capture + prog + avoid_opp + center
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]