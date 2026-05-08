def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    best = None
    best_score = -10**18

    for dx, dy, nx, ny in cand:
        if resources:
            best_adv = -10**9
            best_d = 10**9
            for r in resources:
                if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                    continue
                rx, ry = r[0], r[1]
                if not inb(rx, ry):
                    continue
                myd = man(nx, ny, rx, ry)
                opd = man(ox, oy, rx, ry)
                adv = opd - myd
                if adv > best_adv or (adv == best_adv and myd < best_d):
                    best_adv = adv
                    best_d = myd
            score = best_adv * 10 - best_d
        else:
            score = -man(nx, ny, ox, oy)

        # Small deterministic bias: prefer staying closer to opponent if tied (forces interaction)
        score += -0.01 * man(nx, ny, ox, oy)

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]