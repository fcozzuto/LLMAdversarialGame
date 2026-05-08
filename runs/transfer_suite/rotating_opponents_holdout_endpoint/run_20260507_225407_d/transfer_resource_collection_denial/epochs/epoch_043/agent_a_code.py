def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs

    # Deterministic target selection: prefer resources we can reach no later than opponent.
    best_t = None
    best_val = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) == 2):
            continue
        tx, ty = r[0], r[1]
        if not inb(tx, ty) or (tx, ty) in obs:
            continue
        ds = abs(sx - tx) + abs(sy - ty)
        do = abs(ox - tx) + abs(oy - ty)
        v = (do - ds) * 200 - ds * 3 - do
        if best_val is None or v > best_val or (v == best_val and (tx, ty) < best_t):
            best_val, best_t = v, (tx, ty)

    if best_t is None:
        # If no target, just stay (valid) or move toward open space deterministically.
        for dx, dy in [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    tx, ty = best_t

    # Choose the next step that maximizes our advantage for this target, with obstacle-safe greedy tie-breaks.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds2 = abs(nx - tx) + abs(ny - ty)
        do2 = abs(ox - tx) + abs(oy - ty)
        adv = (do2 - ds2)
        score = adv * 1000 - ds2 * 10
        # Secondary: prefer smaller total travel, then deterministic order by (dx,dy).
        score -= (abs(nx - sx) + abs(ny - sy))
        key = (score, -ds2, -adv, dx, dy)
        if best_score is None or key > best_score:
            best_score = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]