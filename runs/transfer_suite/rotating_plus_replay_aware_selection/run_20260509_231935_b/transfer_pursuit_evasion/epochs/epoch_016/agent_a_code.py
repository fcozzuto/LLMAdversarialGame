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
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_pursuer = ("purs" in sr) and ("evad" not in sr)
    # If roles ambiguous, infer: pursuit_direct opponent archetype usually pursues; we then try to evade.
    if not ("purs" in sr or "evad" in sr) and "purs" in orr:
        self_is_pursuer = False

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def score_move(nx, ny):
        if (nx, ny) in obs:
            return -10**9
        d = dist((nx, ny), (ox, oy))
        if self_is_pursuer:
            # Chase while avoiding obstacles; prefer reducing distance strongly.
            s = -4 * d
        else:
            # Evade: maximize distance, avoid moving toward opponent-aligned corners.
            s = 4 * d
        # Soft obstacle avoidance: penalize adjacent obstacle mass.
        adj_obs = 0
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            ax, ay = nx + dx, ny + dy
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obs:
                adj_obs += 1
        s -= 0.6 * adj_obs

        # Bias target corner for evader (run to the farther corner from opponent).
        if not self_is_pursuer:
            corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
            far_corner = max(corners, key=lambda c: dist(c, (ox, oy)))
            s -= 0.35 * dist((nx, ny), far_corner)
            # Also discourage stepping closer to the opponent than alternatives.
            s += 0.05 * (d - dist((sx, sy), (ox, oy)))
        return s

    best = (0, 0)
    best_s = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        s = score_move(nx, ny)
        if best_s is None or s > best_s or (s == best_s and (dx, dy) < best):
            best_s = s
            best = (dx, dy)
    return [int(best[0]), int(best[1])]