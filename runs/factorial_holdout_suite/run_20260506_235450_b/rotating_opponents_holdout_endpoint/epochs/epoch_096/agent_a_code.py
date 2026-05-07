def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    ap = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    blocked = set()
    for ob in (observation.get("obstacles") or []):
        if isinstance(ob, (list, tuple)) and len(ob) >= 2:
            x, y = int(ob[0]), int(ob[1])
        elif isinstance(ob, dict):
            if "x" in ob and "y" in ob:
                x, y = int(ob["x"]), int(ob["y"])
            else:
                p = ob.get("position")
                if not (isinstance(p, (list, tuple)) and len(p) >= 2):
                    continue
                x, y = int(p[0]), int(p[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            blocked.add((x, y))

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    resources = observation.get("resources") or []
    best = None
    best_score = -10**18

    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            if isinstance(r, dict):
                if "x" in r and "y" in r:
                    x, y = int(r["x"]), int(r["y"])
                else:
                    p = r.get("position")
                    if not (isinstance(p, (list, tuple)) and len(p) >= 2):
                        continue
                    x, y = int(p[0]), int(p[1])
            else:
                continue
        else:
            x, y = int(r[0]), int(r[1])
        if not (0 <= x < w and 0 <= y < h):
            continue
        if (x, y) in blocked:
            continue
        ds = man(sx, sy, x, y)
        do = man(ox, oy, x, y)
        # Prefer resources we can reach sooner than opponent; also prefer being closer overall.
        score = (do - ds) * 100 - ds
        if score > best_score:
            best_score = score
            best = (x, y)

    if best is None:
        return [0, 0]

    tx, ty = best
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in blocked:
                continue
            d = man(nx, ny, tx, ty)
            # Tie-break: avoid stepping into a square too close to opponent (denial pressure).
            dp = man(ox, oy, nx, ny)
            candidates.append((d, -dp, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort()
    return [int(candidates[0][2]), int(candidates[0][3])]