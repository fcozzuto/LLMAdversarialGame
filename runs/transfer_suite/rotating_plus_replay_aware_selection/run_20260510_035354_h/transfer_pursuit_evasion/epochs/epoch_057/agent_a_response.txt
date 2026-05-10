def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    r = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in r) or ("chaser" in r) or ("hunter" in r) or ("catcher" in r)

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def blocked(x, y):
        return (x, y) in obs

    # Determine desired direction (toward or away) with tie-breaking toward reducing boundary hits.
    dx_t = 0 if ox == sx else (1 if ox > sx else -1)
    dy_t = 0 if oy == sy else (1 if oy > sy else -1)
    if not is_pursuer:
        dx_t, dy_t = -dx_t, -dy_t

    # Candidate scoring: prefer legality, then pursue/evade, then avoid obstacles.
    def score(move):
        dx, dy = move
        x, y = sx + dx, sy + dy
        if not inside(x, y) or blocked(x, y):
            return (-10**18, 0, 0)
        d = dist2(x, y)
        # obstacle closeness penalty (deterministic)
        ob_pen = 0
        if obs:
            best = 10**9
            for ax, ay in obs:
                ad = abs(ax - x) + abs(ay - y)
                if ad < best:
                    best = ad
            ob_pen = best
        # pursuer: minimize distance to opponent; evader: maximize
        primary = -d if is_pursuer else d
        # minor: keep away from obstacles if evading, keep away if obstacle blocks might still help pursuer
        secondary = ob_pen if not is_pursuer else -ob_pen
        # minor: prefer not staying if movement exists
        tertiary = -((dx == 0 and dy == 0) * 1)
        return (primary, secondary, tertiary)

    # Prefer step matching desired direction; otherwise best scored move.
    ordered = sorted(moves, key=lambda m: (m[0] != dx_t or m[1] != dy_t, m[0], m[1]))
    best = None
    best_s = None
    for m in ordered:
        s = score(m)
        if best_s is None or s > best_s:
            best_s = s
            best = m
    return [int(best[0]), int(best[1])]