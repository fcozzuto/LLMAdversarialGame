def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    x, y = int(sp[0]), int(sp[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    cells = observation.get("unclaimed_cells")
    if not cells:
        cells = observation.get("resources") or []
    targets = []
    for p in cells:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            tx, ty = int(p[0]), int(p[1])
            if (tx, ty) not in obs and 0 <= tx < w and 0 <= ty < h:
                targets.append((tx, ty))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        if not targets:
            d = (dx, dy)
        else:
            d = min(abs(nx - tx) + abs(ny - ty) for (tx, ty) in targets)
        cand = (d, dx, dy)
        if best is None or cand < best:
            best = cand

    if best is None:
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]
    return [int(best[1]), int(best[2])]