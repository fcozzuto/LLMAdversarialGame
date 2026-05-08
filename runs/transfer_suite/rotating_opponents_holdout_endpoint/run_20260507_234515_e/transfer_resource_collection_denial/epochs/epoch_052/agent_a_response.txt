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
    best_key = None
    if resources:
        for dx, dy, nx, ny in cand:
            best_adv = None
            best_my = None
            best_den = None
            for r in resources:
                if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                    continue
                rx, ry = r[0], r[1]
                if not inb(rx, ry):
                    continue
                myd = man(nx, ny, rx, ry)
                opd = man(ox, oy, rx, ry)
                # primary: win-taking advantage (opponent farther than me)
                adv = opd - myd
                # secondary: prefer closer to that resource
                den = man(nx, ny, ox, oy)  # denier: keep some separation
                key = (adv, -myd, den)
                if best_adv is None or key > (best_adv, -best_my, best_den):
                    best_adv, best_my, best_den = adv, myd, den
            if best_adv is None:
                continue
            # global tie-break: choose move that maximizes advantage, then separation, then closeness
            gkey = (best_adv, best_den, -best_my, dx, dy)
            if best_key is None or gkey > best_key:
                best_key, best = gkey, (dx, dy)
    else:
        # No visible resources: drift toward center while staying away from obstacles
        cx, cy = (w - 1) // 2, (h - 1) // 2
        for dx, dy, nx, ny in cand:
            distc = man(nx, ny, cx, cy)
            disto = 10**9
            for oxp, oyp in obstacles:
                disto = min(disto, man(nx, ny, oxp, oyp))
            gkey = (-distc, disto, dx, dy)
            if best_key is None or gkey > best_key:
                best_key, best = gkey, (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]