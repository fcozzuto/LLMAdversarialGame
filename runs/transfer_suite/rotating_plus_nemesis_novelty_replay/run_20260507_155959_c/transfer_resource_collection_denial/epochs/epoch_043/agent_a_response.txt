def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    obs = set()
    for p in obstacles:
        if len(p) >= 2:
            obs.add((p[0], p[1]))

    if (sx, sy) in obs:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    res = []
    for r in resources:
        if len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    best_target = None
    best_key = None
    for rx, ry in res:
        dself = dist(sx, sy, rx, ry)
        dopp = dist(ox, oy, rx, ry)
        key = (dopp - dself, -dself, -(abs(rx - ox) + abs(ry - oy)))
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    rx, ry = best_target

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dself_new = dist(nx, ny, rx, ry)
        dopp_new = dist(ox, oy, rx, ry)

        # Advantage first (closer than opponent), then speed to capture.
        # Small tie-break: prefer keeping distance from opponent to reduce contest.
        score = ((dopp_new - dself_new), -dself_new, -(dist(nx, ny, ox, oy)))

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]