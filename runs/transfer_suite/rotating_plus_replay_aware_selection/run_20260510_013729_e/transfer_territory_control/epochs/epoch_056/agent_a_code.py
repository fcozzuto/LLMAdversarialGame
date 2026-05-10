def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    x = int(sp[0]); y = int(sp[1])
    ox = int(op[0]); oy = int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    targets = []
    for k in ("unclaimed_cells", "resources"):
        for p in observation.get(k) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                targets.append((int(p[0]), int(p[1])))
        if targets:
            break
    if not targets:
        targets = [((w - 1) // 2, (h - 1) // 2)]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    best = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        tx = min(abs(nx - a) + abs(ny - b) for a, b in targets)
        to_opp = abs(nx - ox) + abs(ny - oy)
        val = (-tx * 10) + to_opp
        if best is None or val > best[0] or (val == best[0] and (dx, dy) < best[1]):
            best = (val, (dx, dy))
    if best is None:
        return [0, 0]
    return [best[1][0], best[1][1]]