def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def bfs(start):
        if start in obs:
            return {}
        dist = {(start[0], start[1]): 0}
        q = [(start[0], start[1])]
        head = 0
        while head < len(q):
            x, y = q[head]
            head += 1
            d = dist[(x, y)]
            nd = d + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs and (nx, ny) not in dist:
                    dist[(nx, ny)] = nd
                    q.append((nx, ny))
        return dist

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    best = None
    best_key = None  # (adv, -do, -ds, ds, rx, ry)
    for rx, ry in resources:
        if (rx, ry) not in ds:
            continue
        dsi = ds[(rx, ry)]
        doi = do.get((rx, ry), 10**9)
        adv = doi - dsi
        key = (adv, -doi, -dsi, dsi, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        return [0, 0]

    tx, ty = best
    # Choose move that leads to the smallest ds to target (deterministic tie-break)
    curd = ds.get((sx, sy), 10**9)
    chosen = [0, 0]
    chosen_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        nd = ds.get((nx, ny), 10**9)
        key = (- (curd - nd), -nd, abs(nx - tx) + abs(ny - ty), dx, dy)
        if chosen_key is None or key > chosen_key:
            chosen_key = key
            chosen = [dx, dy]
    return chosen