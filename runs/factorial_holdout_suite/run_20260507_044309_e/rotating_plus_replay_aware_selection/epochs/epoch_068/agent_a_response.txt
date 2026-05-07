def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs = set(tuple(p) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not resources:
        return [0, 0]

    # If we're already on a resource, stay to ensure collection (engine should handle it).
    if (sx, sy) in obs:
        return [0, 0]
    # Deterministic preference: maximize being closer than opponent; then go sooner.
    opp_pos = (ox, oy)

    def best_key(fromx, fromy):
        best = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            ds = cheb(fromx, fromy, rx, ry)
            do = cheb(opp_pos[0], opp_pos[1], rx, ry)
            adv = do - ds  # positive => we are closer
            # Prefer positive adv; if tied, prefer larger adv; then smaller ds; then deterministic coords.
            # Convert to lexicographic minimization:
            key = (0 if ds <= do else 1, -adv, ds, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        return best[0] if best else (1, 0, 10**9, 0, 0)

    best_move = [0, 0]
    best_key_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        k = best_key(nx, ny)
        if best_key_move is None or k < best_key_move:
            best_key_move = k
            best_move = [dx, dy]

    if best_key_move is None:
        return [0, 0]
    return best_move