def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist_manh(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy
    def near_obst(x, y):
        c = 0
        for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            if (x + ddx, y + ddy) in obst:
                c += 1
        return c

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # If no resources, drift to reduce opponent's options (towards their corner)
    if not resources:
        best = None
        bestv = None
        for dx, dy, nx, ny in legal:
            v = dist_manh(nx, ny, 0, 0) + dist_manh(nx, ny, w - 1, h - 1) * 0
            # Prefer moves that also increase distance between agents
            v += 0.1 * (abs((nx - ox)) + abs((ny - oy)))
            if bestv is None or v < bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Score each move: improve race to nearest resource relative to opponent + obstacle safety + slight central bias
    best_move = (0, 0)
    best_score = None
    for dx, dy, nx, ny in legal:
        ds_self = min(dist_manh(nx, ny, rx, ry) for rx, ry in resources)
        ds_opp = min(dist_manh(ox, oy, rx, ry) for rx, ry in resources)
        ds_self_prev = min(dist_manh(sx, sy, rx, ry) for rx, ry in resources)

        # Determine best resource for opponent after our move (simple approximation: opponent stays)
        # Aim to reduce opponent advantage: (opp dist - self dist)
        race_now = ds_opp - ds_self
        race_prev = ds_opp - ds_self_prev
        improvement = race_now - race_prev

        # Safety and anti-trap: avoid adjacent obstacles heavily
        safety = -2.0 * near_obst(nx, ny)

        # Mild central bias to avoid dead-ends (deterministic)
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_bias = -0.02 * (abs(nx - cx) + abs(ny - cy))

        score = 3.0 * improvement - 1.2 * ds_self + safety + center_bias

        # Deterministic tie-break
        key = (-(score), dx, dy)
        if best_score is None or key < best_score:
            best_score = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]