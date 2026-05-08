def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    targets = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                targets.append((x, y))
    if not targets:
        for p in observation.get("unclaimed_cells") or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                    targets.append((x, y))
            if len(targets) >= 12:
                break
    if not targets:
        targets = [(sx, sy)]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue
        dist_opp = md(nx, ny, ox, oy)
        dist_t = min(md(nx, ny, tx, ty) for tx, ty in targets)
        v = 3 * dist_opp - dist_t
        if best is None or v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]