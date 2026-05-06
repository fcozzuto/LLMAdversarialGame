def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    best_score = -10**18
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        score = (do - ds) * 1000 - ds
        if best is None or score > best_score or (score == best_score and (ds, rx, ry) < best):
            best_score = score
            best = (ds, rx, ry)

    _, tx, ty = best

    dxs = -1 if tx < sx else (1 if tx > sx else 0)
    dys = -1 if ty < sy else (1 if ty > sy else 0)

    candidates = [
        (dxs, dys), (dxs, 0), (0, dys),
        (dxs, -dys), (-dxs, dys), (0, 0)
    ]
    seen = set()
    for dx, dy in candidates:
        if (dx, dy) in seen:
            continue
        seen.add((dx, dy))
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            return [dx, dy]

    return [0, 0]