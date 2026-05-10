def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obs = set()
    for p in obstacles_list:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    res = []
    for r in resources:
        if r is None or len(r) < 2:
            continue
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            res.append((x, y))
    if not res:
        return [0, 0]

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy  # Chebyshev for 8-neighbor movement

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if (0, 0) in dirs:
        pass

    # Pick a target that we can reach earlier (tie-break favors large score gap).
    # Score basis: opp_dist - self_dist, with preference to closer self among ties.
    best_t = None
    best_t_val = None
    for rx, ry in res:
        self_d = dist((sx, sy), (rx, ry))
        opp_d = dist((ox, oy), (rx, ry))
        val = (opp_d - self_d, -self_d)
        if best_t_val is None or val > best_t_val:
            best_t_val = val
            best_t = (rx, ry)

    tx, ty = best_t

    # Obstacle-aware greedy: choose next step that improves our progress to target
    # and widens the gap vs opponent.
    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        self_d_next = dist((nx, ny), (tx, ty))
        self_d_now = dist((sx, sy), (tx, ty))
        opp_d_now = dist((ox, oy), (tx, ty))
        opp_can_follow = dist((ox, oy), (tx, ty))  # deterministic proxy (opponent not simulated)

        # Encourage reducing our distance; also discourage letting opponent get strictly closer.
        gap_now = opp_d_now - dist((sx, sy), (tx, ty))
        gap_next = opp_can_follow - self_d_next

        # Small penalty for staying to avoid deadlocks.
        stay_pen = 1 if (dx == 0 and dy == 0) else 0

        val = (gap_next - gap_now, self_d_now - self_d_next, -self_d_next, -stay_pen)
        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    return best if best is not None else [0, 0]