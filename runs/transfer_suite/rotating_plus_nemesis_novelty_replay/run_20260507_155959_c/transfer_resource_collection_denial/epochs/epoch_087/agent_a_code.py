def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny) and (dx != 0 or dy != 0 or (nx, ny) != (sx, sy)):
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    target_list = res if res else [(ox, oy)]
    best = None
    best_score = None

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) == (ox, oy):
            continue
        md = 10**9
        for rx, ry in target_list:
            if (rx, ry) in obs:
                continue
            d = dist(nx, ny, rx, ry)
            if d < md:
                md = d
        score = md
        if observation.get("remaining_resource_count") is not None:
            rc = observation.get("remaining_resource_count", 0)
            if isinstance(rc, int) and rc <= 2 and res:
                score = md * 2 - dist(nx, ny, ox, oy)
        if best is None or score < best_score or (score == best_score and (dx, dy) < best):
            best, best_score = (dx, dy), score

    if best is None:
        best = min(moves)
    return [int(best[0]), int(best[1])]