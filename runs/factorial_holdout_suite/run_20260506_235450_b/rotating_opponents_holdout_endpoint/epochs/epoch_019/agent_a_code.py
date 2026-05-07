def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for a in (observation.get("obstacles") or []):
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obs.add((int(a[0]), int(a[1])))
        elif isinstance(a, dict) and "x" in a and "y" in a:
            obs.add((int(a["x"]), int(a["y"])))

    def parse_xy(r):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return int(r[0]), int(r[1])
        if isinstance(r, dict) and "x" in r and "y" in r:
            return int(r["x"]), int(r["y"])
        return None

    resources = []
    for r in (observation.get("resources") or []):
        p = parse_xy(r)
        if p is not None:
            resources.append(p)

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    actions = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # Pick a target where we are ahead; if none ahead, pick the one that hurts the opponent most.
    best_r = None
    best_r_key = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        ahead = od - sd  # positive means we are closer
        # Prefer being clearly ahead; otherwise prefer closest to us while still competitive.
        key = (ahead, -sd, -od)
        if best_r_key is None or key > best_r_key:
            best_r_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    best_a = (0, 0)
    best_val = None
    for dx, dy in actions:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        sd2 = man(nx, ny, rx, ry)
        od2 = man(nx, ny, ox, oy)
        # Avoid getting stuck: penalize moving into/near obstacles.
        near_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in obs:
                    near_obs += 1
        val = (-sd2) + 0.35 * od2 - 0.08 * near_obs + 0.02 * (-abs(nx - cx) - abs(ny - cy))
        if best_val is None or val > best_val:
            best_val = val
            best_a = (dx, dy)

    return [int(best_a[0]), int(best_a[1])]