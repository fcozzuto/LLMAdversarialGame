def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_key = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        dist_from_us = sd
        dist_from_opp = od
        # Advantage primary; then we prefer closer; then prefer farther from opponent to reduce contest.
        key = (od - sd, -dist_from_us, dist_from_opp, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Simple obstacle-aware nudge: if the direct step is into an obstacle, try axis-first.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # Prefer the axis that reduces Manhattan distance most.
        cand = []
        cand.append((0, 1 if ty > sy else (-1 if ty < sy else 0)))
        cand.append((1 if tx > sx else (-1 if tx < sx else 0), 0))
        cand.append((0, 0))
        best_move = [0, 0]
        best_d = None
        for cdx, cdy in cand:
            px, py = sx + cdx, sy + cdy
            if 0 <= px < w and 0 <= py < h and (px, py) not in obstacles:
                d = md(px, py, tx, ty)
                if best_d is None or d < best_d or (d == best_d and (cdx, cdy) > (best_move[0], best_move[1])):
                    best_d = d
                    best_move = [cdx, cdy]
        return best_move

    return [dx, dy]