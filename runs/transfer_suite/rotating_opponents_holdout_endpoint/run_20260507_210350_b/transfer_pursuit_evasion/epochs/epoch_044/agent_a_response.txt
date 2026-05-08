def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or ("hunt" in self_role) or ("seek" in self_role) or ("chase" in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = abs(x2 - x1); dy = abs(y2 - y1)
        return dx if dx > dy else dy
    def clamp_step(a, b):
        return 0 if a == b else (1 if b > a else -1)

    # Deterministic tie-break order: fixed move list.
    best = None
    best_score = None

    # Predict opponent next (1-step toward/away not exact, but improves determinism)
    px = ox + clamp_step(ox, sx)
    py = oy + clamp_step(oy, sy)
    if not (0 <= px < w): px = ox
    if not (0 <= py < h): py = oy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Slight preference for staying away from obstacles by penalizing being adjacent
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0: 
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    adj_obs += 1

        d_now = cheb(nx, ny, ox, oy)
        d_pred = cheb(nx, ny, px, py)

        if is_pursuer:
            # Maximize negative distance (i.e., minimize distance); prefer blocking/predictive move
            score = -(2.0 * d_pred + 1.0 * d_now) - 0.2 * adj_obs
        else:
            # Evader: maximize distance to current/predicted pursuer
            score = (2.0 * d_pred + 1.0 * d_now) - 0.2 * adj_obs

        if best is None or (score > best_score) or (score == best_score and (dx, dy) < best):
            best = (dx, dy)
            best_score = score

    if best is None:
        # If all blocked (rare), stay put.
        return [0, 0]
    return [best[0], best[1]]