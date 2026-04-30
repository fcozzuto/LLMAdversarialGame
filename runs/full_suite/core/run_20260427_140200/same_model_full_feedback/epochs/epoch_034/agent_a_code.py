def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0), (1, -1), (1, 1), (-1, 1), (-1, -1)]
    if resources:
        best = None
        bestd = None
        for rx, ry in resources:
            d = abs(rx - sx) + abs(ry - sy)
            if bestd is None or d < bestd or (d == bestd and (rx, ry) < best):
                bestd = d
                best = (rx, ry)
        tx, ty = best
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        preferred = [(dx, dy), (dx, 0), (0, dy)]
        seen = set()
        cand = []
        for a, b in preferred + dirs:
            if (a, b) in seen:
                continue
            seen.add((a, b))
            if a in (-1, 0, 1) and b in (-1, 0, 1) and (a != 0 or b != 0):
                cand.append((a, b))
        for a, b in cand:
            nx, ny = sx + a, sy + b
            if ok(nx, ny):
                return [a, b]
    # No resources: move to reduce distance to opponent with obstacle-aware tie-break
    dx = 0 if ox == sx else (1 if ox > sx else -1)
    dy = 0 if oy == sy else (1 if oy > sy else -1)
    preferred = [(dx, dy), (dx, 0), (0, dy), (-dx, 0), (0, -dy), (0, 1), (0, -1), (1, 0), (-1, 0)]
    seen = set()
    cand = []
    for a, b in preferred + dirs:
        if (a, b) in seen:
            continue
        seen.add((a, b))
        if a in (-1, 0, 1) and b in (-1, 0, 1) and (a != 0 or b != 0):
            cand.append((a, b))
    best = None
    bestd = None
    for a, b in cand:
        nx, ny = sx + a, sy + b
        if not ok(nx, ny):
            continue
        d = abs(ox - nx) + abs(oy - ny)
        if bestd is None or d < bestd or (d == bestd and (nx, ny) < best):
            bestd = d
            best = (nx, ny)
            bestmove = [a, b]
    return bestmove if best is not None else [0, -1]