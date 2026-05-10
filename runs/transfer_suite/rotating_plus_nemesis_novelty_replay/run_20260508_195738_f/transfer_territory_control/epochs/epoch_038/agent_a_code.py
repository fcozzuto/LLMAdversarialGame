def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs
    resources = observation.get("resources", []) or []
    target = (ox, oy)
    if resources:
        best = None
        bx, by = target
        for p in resources:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                rx, ry = int(p[0]), int(p[1])
                d = abs(x - rx) + abs(y - ry)
                if best is None or d < best:
                    best = d
                    bx, by = rx, ry
        target = (bx, by)
    tx, ty = target
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = int(x + dx), int(y + dy)
        if not inb(nx, ny):
            continue
        dist = abs(nx - tx) + abs(ny - ty)
        opp_dist = abs(nx - ox) + abs(ny - oy)
        score = dist * 10 - opp_dist
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]