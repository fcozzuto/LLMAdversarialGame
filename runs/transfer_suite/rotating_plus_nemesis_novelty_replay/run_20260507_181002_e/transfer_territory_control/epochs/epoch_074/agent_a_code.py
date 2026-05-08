def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = set(resources)
    if not unclaimed:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx, ty = cx, cy
    else:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

        def man(a, b, c, d):
            return abs(a - c) + abs(b - d)

        best = None
        best_val = -10**18
        # deterministic scan order: sort by (x,y)
        for tx, ty in sorted(unclaimed):
            if (tx, ty) in obstacles:
                continue
            ds = man(sx, sy, tx, ty)
            do = man(ox, oy, tx, ty)
            center_bias = -(abs(tx - cx) + abs(ty - cy)) * 0.25
            # prefer cells we can reach first; small penalty if opponent already controls nearby
            near_opp = 1 if any((abs(tx - px) <= 1 and abs(ty - py) <= 1) for (px, py) in oppT) else 0
            val = (do - ds) * 2.0 + center_bias - near_opp * 0.5 - ds * 0.05
            # extra preference for frontier growth: near our territory but not near theirs
            near_self = 1 if any((abs(tx - px) <= 1 and abs(ty - py) <= 1) for (px, py) in selfT) else 0
            val += near_self * 0.6
            if val > best_val:
                best_val = val
                best = (tx, ty)
        tx, ty = best if best is not None else (int(cx), int(cy))

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # if diagonal is blocked by obstacle, fall back to axis-aligned step deterministically
    diag = (sx + dx, sy + dy)
    if dx != 0 and dy != 0 and diag in obstacles:
        if (sx + dx, sy) not in obstacles:
            dy = 0
        elif (sx, sy + dy) not in obstacles:
            dx = 0
        else:
            dx = 0
            dy = 0

    return [int(dx), int(dy)]