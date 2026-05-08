def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst

    resources = observation.get("resources") or []
    targets = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                targets.append((x, y))

    if targets:
        tx, ty = min(targets, key=lambda t: (t[0] - sx) * (t[0] - sx) + (t[1] - sy) * (t[1] - sy))
    else:
        tx, ty = ox, oy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    best = None
    bestd = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        if bestd is None or d < bestd:
            bestd = d
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]