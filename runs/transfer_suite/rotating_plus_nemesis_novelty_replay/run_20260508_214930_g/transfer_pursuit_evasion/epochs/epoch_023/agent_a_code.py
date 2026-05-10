def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            obs.add((int(b[0]), int(b[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    # Predict evader moving away from pursuer (zigzag-like: often alternates away).
    away_x = 0 if ox == sx else (1 if ox > sx else -1)
    away_y = 0 if oy == sy else (1 if oy > sy else -1)
    px, py = ox + away_x, oy + away_y
    if not valid(px, py):
        px, py = ox, oy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best = None
    # Tie-breaker: prefer moves that also reduce direct distance to current opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_pred = dist2(nx, ny, px, py)
        d_now = dist2(nx, ny, ox, oy)
        # Secondary tie: stay away from nearest obstacle (deterministic, helps avoid dead ends).
        if obs:
            min_obs = 10**9
            for bx, by in obs:
                cd = abs(nx - bx) if abs(nx - bx) > abs(ny - by) else abs(ny - by)
                if cd < min_obs:
                    min_obs = cd
        else:
            min_obs = 10**9
        key = (d_pred, d_now, -min_obs, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]