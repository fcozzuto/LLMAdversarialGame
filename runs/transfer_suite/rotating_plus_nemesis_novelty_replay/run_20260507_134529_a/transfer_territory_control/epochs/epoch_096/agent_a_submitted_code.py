def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except Exception:
        sx, sy, ox, oy = 0, 0, w - 1, h - 1

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            obstacles.add((x, y))
        except Exception:
            pass

    resources = set()
    for p in observation.get("resources") or []:
        try:
            x, y = int(p[0]), int(p[1])
            resources.add((x, y))
        except Exception:
            pass

    # If provided, use territorial denial; else, fall back to resources/opp.
    self_terr = set()
    for p in observation.get("self_territory") or []:
        try:
            self_terr.add((int(p[0]), int(p[1])))
        except Exception:
            pass
    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        try:
            opp_terr.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        try:
            unclaimed.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Determine simple mode: if trailing, chase resources/unclaimed near opponent; else deny opponent territory.
    score_self = len(self_terr)
    score_opp = len(opp_terr)
    trailing = score_self <= score_opp

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    targets = []
    if resources:
        targets = list(resources)
    elif unclaimed:
        # Prefer unclaimed closer to opponent
        tmp = sorted(unclaimed, key=lambda p: dist2(p[0], p[1], ox, oy))
        targets = tmp[: min(10, len(tmp))]
    else:
        targets = [(ox, oy)]

    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        d_to_nearest = min(dist2(nx, ny, tx, ty) for tx, ty in targets) if targets else dist2(nx, ny, ox, oy)
        val = -d_to_nearest

        if (nx, ny) in resources:
            val += 5000
        if trailing:
            if (nx, ny) in unclaimed:
                val += 1200
            if (nx, ny) in opp_terr:
                val -= 600
        else:
            if (nx, ny) in opp_terr:
                val += 2000
            if (nx, ny) in unclaimed:
                val += 300
            if (nx, ny) in self_terr:
                val -= 150

        # Small preference for progressing toward opponent to break ties deterministically
        val += -dist2(nx, ny, ox, oy) // 5

        if best is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best