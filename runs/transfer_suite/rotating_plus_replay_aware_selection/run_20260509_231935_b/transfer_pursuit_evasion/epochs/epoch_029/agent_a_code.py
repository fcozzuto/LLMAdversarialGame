def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obs.add((int(x), int(y)))
        except:
            pass

    sr = str(observation.get("self_role", "")).lower()
    self_is_evader = ("evad" in sr)
    # If we can't tell, assume pursuer (better for scoring since capture ends).
    is_evader = self_is_evader

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return in_bounds(x, y) and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    best_score = None
    best_move = [0, 0]

    # Tie-breakers: prefer moves with higher mobility (more options).
    def mobility(x, y):
        m = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if safe(nx, ny):
                m += 1
        return m

    # Additional tie-breaker: stay closer to center to avoid corner-sticking for pursuer.
    def center_bias(x, y):
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        return dist2(x, y, cx, cy)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue

        if not is_evader:
            # Pursuer: capture immediately if landing on opponent (capture_radius=0).
            if nx == ox and ny == oy:
                return [dx, dy]
            # Otherwise, minimize distance; avoid being blocked by obstacles via mobility bonus.
            score = -dist2(nx, ny, ox, oy) + 0.01 * mobility(nx, ny) - 0.001 * center_bias(nx, ny)
        else:
            # Evader: maximize distance; also prefer moves that don't trap against obstacles/bounds.
            score = dist2(nx, ny, ox, oy) + 0.01 * mobility(nx, ny) - 0.001 * center_bias(nx, ny)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move