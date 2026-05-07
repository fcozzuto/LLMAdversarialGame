def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and in_bounds(x, y):
                obs.add((x, y))

    if not (isinstance(sx, int) and isinstance(sy, int) and in_bounds(sx, sy)):
        return [0, 0]
    if not (isinstance(ox, int) and isinstance(oy, int) and in_bounds(ox, oy)):
        ox, oy = 0, 0
    resources2 = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and in_bounds(x, y) and (x, y) not in obs:
                resources2.append((x, y))
    if not resources2:
        return [0, 0]

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick target that favors being first or, if denied, minimizes how much we lag while moving in a direction that doesn't help the opponent.
    best = None
    best_key = None
    for tx, ty in resources2:
        md = manh(sx, sy, tx, ty)
        od = manh(ox, oy, tx, ty)
        # If we are not behind, prioritize race advantage strongly; otherwise, still try to reduce lag and avoid "handing" closer access.
        behind = 1 if md > od else 0
        race = (od - md)
        # Slight preference for farther resources when tied, to avoid trivial near grabs that denier can mirror.
        dist_pref = md
        key = (behind, -race, dist_pref)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best

    # Choose a move step that reduces distance to target while keeping out of obstacles/bounds.
    best_move = [0, 0]
    best_val = None
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue
        my_d = manh(nx, ny, tx, ty)

        # Opponent response: discourage moves that bring us closer to resources the opponent is also very near.
        opp_to_target = manh(ox, oy, tx, ty)
        # Encourage blocking-ish behavior: if opponent is closer to the target, reduce our distance to opponent (so they must deviate) only mildly.
        opp_prox = manh(nx, ny, ox, oy)

        # Main objective: minimize distance to target (and secondarily avoid letting opponent get there first).
        val = (0, my_d, 0 if md <= od else 1, opp_prox, opp_to_target)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move