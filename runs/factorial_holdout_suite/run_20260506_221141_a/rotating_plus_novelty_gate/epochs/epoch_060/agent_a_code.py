def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in (observation.get("obstacles") or []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in (observation.get("resources") or []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**30

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        if resources:
            md2 = None
            for rx, ry in resources:
                d2 = (nx - rx) * (nx - rx) + (ny - ry) * (ny - ry)
                if md2 is None or d2 < md2:
                    md2 = d2
            if md2 is None:
                md2 = 10**12
            pod2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            score = (-md2) + (pod2 // 10)
        else:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            dc2 = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            pod2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            score = (pod2 // 10) - dc2

        if score > best_score or (score == best_score and (best is None or (dx, dy) < best)):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]