def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    oppT = set()
    for p in (observation.get("opponent_territory") or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                oppT.add((x, y))

    myT = set()
    for p in (observation.get("self_territory") or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                myT.add((x, y))

    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    def best_dist_to_resources():
        if not res:
            return None
        best = None
        bd = 10**18
        for x, y in res:
            if (x, y) in obs:
                continue
            d = abs(sx - x) + abs(sy - y)
            if d < bd:
                bd, best = d, (x, y)
        return best

    target = best_dist_to_resources()
    if target is None:
        target = (ox, oy)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1), (0, 0)]
    best_move = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        # Prefer expanding into unclaimed; avoid opponent territory.
        score = 0
        if (nx, ny) in oppT:
            score -= 10**6
        if (nx, ny) in unclaimed:
            score += 50
        if (nx, ny) in myT:
            score += 5

        # Move closer to target.
        d = abs(nx - target[0]) + abs(ny - target[1])
        score -= d * 2

        # Small preference to not get stuck (stay only if needed).
        if dx == 0 and dy == 0:
            score -= 3

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move