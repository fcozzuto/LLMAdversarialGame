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
        # Drift to best corner (prefer away from opponent to reduce contest)
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        for cx, cy in corners:
            if (cx, cy) in obstacles:
                continue
            sd = abs(cx - sx) + abs(cy - sy)
            od = abs(cx - ox) + abs(cy - oy)
            score = (od - sd, -sd)  # maximize advantage
            if best is None or score > best[0]:
                best = (score, cx, cy)
        if best is None:
            return [0, 0]
        _, tx, ty = best
    else:
        # Pick resource: smallest self distance; break ties by maximizing opponent distance
        best = None
        for rx, ry in resources:
            sd = abs(rx - sx) + abs(ry - sy)
            od = abs(rx - ox) + abs(ry - oy)
            # primary: minimize sd; secondary: maximize od; tertiary: deterministic by coord
            key = (sd, -od, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        _, tx, ty = best

    # Choose one-step move to reduce distance to target while avoiding obstacles
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # deterministic ordering already fixed by list above
    bestm = None
    for dx, dy in deltas:
        nx = sx + dx; ny = sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = abs(tx - nx) + abs(ty - ny)
        cd = abs(tx - sx) + abs(ty - sy)
        # Encourage progress; if no progress possible, minimize distance anyway
        progress = (cd - nd)
        od_after = abs(tx - ox - dx) + abs(ty - oy - dy)  # rough, deterministic proxy
        # maximize progress, then (self distance), then safety vs opponent proxy, then lexicographic on move
        score = (progress, -nd, od_after, -dx, -dy)
        if bestm is None or score > bestm[0]:
            bestm = (score, dx, dy)

    if bestm is None:
        return [0, 0]
    return [int(bestm[1]), int(bestm[2])]