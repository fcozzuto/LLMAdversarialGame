def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def centroid(cset, fallback):
        if not cset:
            return fallback
        ax = ay = 0
        for x, y in cset:
            ax += x
            ay += y
        n = len(cset)
        return ax // n, ay // n

    sset = set(map(tuple, observation.get("self_territory") or []))
    oset = set(map(tuple, observation.get("opponent_territory") or []))
    sc = int(observation.get("self_territory_count") or 0)
    oc = int(observation.get("opponent_territory_count") or 0)
    if sc == 0 and oc == 0:
        scores = observation.get("scores") or {}
        if isinstance(scores, dict):
            sc = int(scores.get("self") or scores.get("me") or 0)
            oc = int(scores.get("opponent") or scores.get("op") or 0)

    behind = oc > sc
    if behind:
        tx, ty = ox, oy
    else:
        tx, ty = centroid(sset, (sx, sy))

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0)]
    best = None
    bestv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = abs(nx - tx) + abs(ny - ty)
        v = -d if behind else d
        if best is None or v > bestv:
            best = (dx, dy)
            bestv = v
    if best is None:
        return [0, 0]
    return [best[0], best[1]]