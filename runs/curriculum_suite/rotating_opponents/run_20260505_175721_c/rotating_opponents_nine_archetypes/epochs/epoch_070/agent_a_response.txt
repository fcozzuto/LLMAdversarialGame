def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax + ay

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    # Target resources: nearest-to-opponent first (edge_patrol pressure), but prioritize those we can beat.
    pairs = []
    for rx, ry in resources:
        od = man(ox, oy, rx, ry)
        sd = man(sx, sy, rx, ry)
        pairs.append((od, sd, rx, ry))
    pairs.sort(key=lambda t: (t[0], -t[1]))

    best = None
    best_key = None
    for dx, dy, nx, ny in cand:
        # Score after our move against top few targets
        score = 0
        min_self = 10**9
        min_opp = 10**9
        for i in range(6 if len(pairs) >= 6 else len(pairs)):
            od, sd0, rx, ry = pairs[i]
            sd = man(nx, ny, rx, ry)
            if sd < min_self: min_self = sd
            if od < min_opp: min_opp = od
            # Intercept bonus if we can reach no later than opponent (or reduce their margin)
            adv = od - sd
            # Also value reducing our distance to the best remaining resource
            score += (adv * 3) + (-sd)
        # Prefer moves that also push towards center for smoother edge patrol responses
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score += -man(nx, ny, int(cx), int(cy)) * 0.2
        key = (score, -min_self, min_opp, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)
    return [int(best[0]), int(best[1])]