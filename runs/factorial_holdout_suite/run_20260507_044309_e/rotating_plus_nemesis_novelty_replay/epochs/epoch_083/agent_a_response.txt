def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not res:
        return [0, 0]

    turns = observation.get("turns_remaining", 1)
    # If near end, just grab nearest to avoid losing.
    aggressive = 1 if turns > 8 else 0

    best = None  # (value, tx, ty)
    for tx, ty in res:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer resources we can reach strictly earlier, otherwise race by distance.
        # Add slight bonus for being farther along our direction (ties broken deterministically).
        val = (do - ds) * (2 if aggressive else 1) - 0.1 * ds
        # Deterministic tie-break
        cand = (val, -tx, -ty)
        if best is None or cand > (best[0], -best[1], -best[2]):
            best = (val, tx, ty)

    _, tx, ty = best

    # Choose move: step that advances toward target, with obstacle avoidance.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            # Strong preference to reduce distance to chosen target.
            d = cheb(nx, ny, tx, ty)
            # Mild anti-collision: discourage moving closer to opponent if tie.
            opp_d = cheb(nx, ny, ox, oy)
            score = (-(d), (opp_d), -abs(nx - ox), -abs(ny - oy), dx, dy)
            moves.append((score, dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    moves.sort(reverse=True)
    _, dx, dy, _, _ = moves[0]

    # If best step doesn't reduce our distance (rare due to obstacle), stay.
    if cheb(sx, sy, tx, ty) <= cheb(sx + dx, sy + dy, tx, ty):
        return [0, 0]
    return [dx, dy]