def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        # deterministic: head to nearest free corner
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        for cx, cy in corners:
            if (cx, cy) in obstacles:
                continue
            d = abs(cx - sx) + abs(cy - sy)
            tieb = (observation.get("turn_index", 0) or 0) % 4
            key = (d, (cx + cy + tieb) % 7)
            if best is None or key < best[0]:
                best = (key, cx, cy)
        if best is None:
            return [0, 0]
        cx, cy = best[1], best[2]
    else:
        # choose resource we can "arrive" at first; favor closer + harder for opponent
        ti = int(observation.get("turn_index", 0) or 0)
        best = None
        for rx, ry in resources:
            ds = max(abs(rx - sx), abs(ry - sy))  # king distance
            do = max(abs(rx - ox), abs(ry - oy))
            # if we can't beat them, downweight; still allow if it yields the best eventual path
            if ds == 0:
                score = 1e9
            else:
                score = -ds
                if ds <= do:
                    score += 2.0
                else:
                    score -= 1.5 * (ds - do)
                # slight bias to break ties deterministically
                score += 0.01 * (((rx + 3 * ry + ti) % 11) - 5)
            # prefer closer in raw distance after score
            key = (-score, ds, do, (rx + ry) % 9)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        cx, cy = best[1], best[2]

    dx = 0 if cx == sx else (1 if cx > sx else -1)
    dy = 0 if cy == sy else (1 if cy > sy else -1)

    # validate candidate; if blocked, try alternate step ordering deterministically
    candidates = []
    candidates.append((dx, dy))
    candidates.append((dx, 0))
    candidates.append((0, dy))
    candidates.append((0, 0))
    # small deterministic diagonal adjustment when both nonzero
    if dx != 0 and dy != 0:
        candidates.append((dx, -dy))
        candidates.append((-dx, dy))

    for ndx, ndy in candidates:
        nx, ny = sx + ndx, sy + ndy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(ndx), int(ndy)]
    return [0, 0]