def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    ap = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
        else:
            try:
                x, y = int(a.get("x")), int(a.get("y"))
            except Exception:
                continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        else:
            try:
                x, y = int(r.get("x")), int(r.get("y"))
            except Exception:
                continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    for (rx, ry) in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach earlier; if tied, prefer closer to us; then deterministic lex.
        key = (od - sd, -sd, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)

    _, tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    cand = []
    # Try the most direct diagonal/axis steps first, then alternatives.
    for mx in (dx, 0, -dx):
        for my in (dy, 0, -dy):
            if (mx, my) == (0, 0):
                continue
            cand.append((mx, my))
    cand.append((dx, dy))
    cand.append((dx, 0))
    cand.append((0, dy))
    cand.append((0, 0))

    seen = set()
    for mx, my in cand:
        if (mx, my) in seen:
            continue
        seen.add((mx, my))
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [mx, my]

    return [0, 0]