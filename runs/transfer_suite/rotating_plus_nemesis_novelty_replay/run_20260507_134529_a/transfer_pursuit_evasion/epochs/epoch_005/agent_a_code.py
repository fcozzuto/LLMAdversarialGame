def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    roles = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    is_pursuer = ("pursuer" in roles) or ("evader" not in roles)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def clamp(x, y):
        x = 0 if x < 0 else (w - 1 if x >= w else x)
        y = 0 if y < 0 else (h - 1 if y >= h else y)
        if (x, y) in obs:
            return sx, sy
        return x, y

    def cheb(x, y, tx, ty):
        dx = abs(tx - x)
        dy = abs(ty - y)
        return dx if dx > dy else dy

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    best = None
    best_score = None
    # Deterministic tie-break: fixed scan order already from dx/dy loops
    for dx, dy, nx, ny in moves:
        d_opp = cheb(nx, ny, ox, oy)
        if is_pursuer:
            score = (-d_opp, -cheb(nx, ny, far_corner[0], far_corner[1]))
        else:
            # Prefer moving away and breaking toward the farthest corner
            score = (d_opp, -cheb(nx, ny, far_corner[0], far_corner[1]))
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]