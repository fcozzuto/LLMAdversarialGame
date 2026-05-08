def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]
    res = [(r[0], r[1]) for r in resources if inb(r[0], r[1]) and (r[0], r[1]) not in obs]
    if not res:
        return [0, 0]
    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)
    # Pick a target resource that we can reach sooner than the opponent.
    best_t = None
    best_k = None
    for rx, ry in res:
        du = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        # Tie-break: prefer closer + harder for opponent.
        k = (du - do, du, rx, ry)
        if best_k is None or k < best_k:
            best_k = k
            best_t = (rx, ry)
    tx, ty = best_t
    # Predict opponent next step greedily toward the target (deterministic).
    def opp_step(px, py):
        best = (10**9, 0, 0)
        chosen = (0, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = px + dx, py + dy
                if inb(nx, ny) and (nx, ny) not in obs:
                    d = md(nx, ny, tx, ty)
                    key = (d, abs(dx) + abs(dy), dx, dy)
                    if key < best:
                        best = key
                        chosen = (dx, dy)
        return chosen
    odx, ody = opp_step(ox, oy)
    nox, noy = ox + odx, oy + ody
    # Score our candidate moves by estimated reach advantage after opponent moves.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in legal:
        nsx, nsy = sx + dx, sy + dy
        du = md(nsx, nsy, tx, ty)
        do = md(nox, noy, tx, ty)
        # Encourage moving onto the target immediately; discourage letting opponent catch up.
        val = (do - du) * 10 - du + (2 if (nsx, nsy) == (tx, ty) else 0)
        # Small deterministic preference to reduce dithering.
        val -= (abs(dx) + abs(dy)) * 0.01
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]