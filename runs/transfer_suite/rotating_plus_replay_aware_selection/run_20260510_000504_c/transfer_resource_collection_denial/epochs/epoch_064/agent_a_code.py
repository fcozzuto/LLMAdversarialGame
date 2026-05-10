def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            q = p.get("position", p)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                obstacles.add((int(q[0]), int(q[1])))
            elif "x" in p and "y" in p:
                obstacles.add((int(p["x"]), int(p["y"])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            q = r.get("position", r)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                resources.append((int(q[0]), int(q[1])))
            elif "x" in r and "y" in r:
                resources.append((int(r["x"]), int(r["y"])))

    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        d = abs(rx - sx) + abs(ry - sy)
        if best is None or d < best[0] or (d == best[0] and (rx, ry) < best[1]):
            best = (d, (rx, ry))
    tx, ty = best[1]

    dx = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    dy = 0
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    moves = [(dx, 0), (0, dy), (dx, dy), (0, 0)]
    for cx, cy in moves:
        nx, ny = sx + cx, sy + cy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            if cx == 0 and cy == 0 and len(resources) > 1:
                return [dx, dy]
            return [int(cx), int(cy)]

    for cx in (-1, 0, 1):
        for cy in (-1, 0, 1):
            if cx == 0 and cy == 0:
                continue
            nx, ny = sx + cx, sy + cy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [int(cx), int(cy)]

    return [0, 0]