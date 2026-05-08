def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = observation.get("obstacles", []) or []
    obstacles = set()
    for o in obs:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = observation.get("resources", []) or []
    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                targets.append((x, y))

    tx, ty = (ox, oy)
    if targets:
        best = None
        bestd = None
        for x, y in targets:
            d = abs(x - sx) + abs(y - sy)
            if bestd is None or d < bestd or (d == bestd and (x, y) < best):
                bestd = d
                best = (x, y)
        tx, ty = best

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = abs(nx - tx) + abs(ny - ty)
        score = -dist
        if (best_score is None) or (score > best_score) or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [dx, dy]