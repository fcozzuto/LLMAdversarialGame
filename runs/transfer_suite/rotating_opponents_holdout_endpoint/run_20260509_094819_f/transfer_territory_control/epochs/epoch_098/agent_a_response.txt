def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    candidates = []
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    resources = observation.get("resources") or []

    for t in unclaimed:
        if t and len(t) >= 2:
            tx, ty = int(t[0]), int(t[1])
            if (tx, ty) in obstacles:
                continue
            ds = abs(tx - sx) + abs(ty - sy)
            do = abs(tx - ox) + abs(ty - oy)
            adv = do - ds  # positive means we are closer
            center = -(abs(tx - cx) + abs(ty - cy))
            edge = 1 if (tx == 0 or tx == w - 1 or ty == 0 or ty == h - 1) else 0
            # Prefer taking nearby unclaimed we can reach first, and move toward center to pressure.
            score = adv * 1000 + center * 3 + edge * 2 - (tx + ty) * 0.001
            candidates.append((score, tx, ty))

    # If no unclaimed, steer toward center while avoiding obvious obstacle cells by simple step choice.
    if not candidates:
        tx, ty = int(round(cx)), int(round(cy))
    else:
        # Deterministic: sort by score desc, then tx,ty asc.
        candidates.sort(key=lambda z: (-z[0], z[1], z[2]))
        tx, ty = candidates[0][1], candidates[0][2]

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # Deterministically try axis moves before staying.
        if dx != 0 and (sx + dx, sy) not in obstacles:
            return [dx, 0]
        if dy != 0 and (sx, sy + dy) not in obstacles:
            return [0, dy]
        return [0, 0]
    return [dx, dy]