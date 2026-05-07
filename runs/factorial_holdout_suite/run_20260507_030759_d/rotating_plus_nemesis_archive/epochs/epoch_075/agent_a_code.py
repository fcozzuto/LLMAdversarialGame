def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    best_key = None
    for rx, ry in resources:
        self_d = man(sx, sy, rx, ry)
        opp_d = man(ox, oy, rx, ry)
        adv = opp_d - self_d  # positive => we are closer
        # Encourage definite lead; if no lead, race nearest-for-us.
        lead_bonus = 1000 if adv > 0 else 0
        value = (adv * 100 + lead_bonus) - self_d
        key = (-value, abs(adv), self_d, rx + ry, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obst or not (0 <= nx < w and 0 <= ny < h):
        # Try orthogonal alternatives deterministically
        candidates = []
        candidates.append((dx, 0))
        candidates.append((0, dy))
        candidates.append((0, 0))
        # Prefer the alternative that still reduces our distance to target
        best2 = None
        best2_key = None
        for cdx, cdy in candidates:
            cx, cy = sx + cdx, sy + cdy
            if not (0 <= cx < w and 0 <= cy < h) or (cx, cy) in obst:
                continue
            d2 = man(cx, cy, tx, ty)
            key2 = (d2, abs(cdx), abs(cdy), cdx, cdy)
            if best2_key is None or key2 < best2_key:
                best2_key = key2
                best2 = (cdx, cdy)
        if best2 is None:
            return [0, 0]
        return [best2[0], best2[1]]

    return [dx, dy]