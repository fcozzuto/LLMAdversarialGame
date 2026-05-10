def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        obs.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_pursuer = ("purs" in role) or ("purs" in opp_role and "evad" in role == False)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def score(nx, ny):
        if (nx, ny) in obs:
            return -10**9 if is_pursuer else -10**9

        d = cheb(nx, ny, ox, oy)

        # Obstacle/edge pressure to reduce getting stuck against walls
        edge_pen = 0
        if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
            edge_pen = 1 if not is_pursuer else -1

        adj_obs = 0
        for ax, ay in obs:
            if abs(nx - ax) <= 1 and abs(ny - ay) <= 1 and (nx, ny) != (ax, ay):
                adj_obs += 1

        # Small bias toward/away from opponent's side
        if not is_pursuer:
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            tx, ty = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
            bias = cheb(nx, ny, tx, ty)
            return d * 1000 + bias * 3 - adj_obs * 5 + edge_pen
        else:
            return -d * 1000 - adj_obs * 5 + edge_pen

    best = None
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        sc = score(nx, ny)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]