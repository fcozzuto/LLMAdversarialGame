def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    unclaimed = observation.get("unclaimed_cells", []) or []
    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Target priority: unclaimed -> opponent territory -> opponent position
    opp_terr = observation.get("opponent_territory", []) or []
    if unclaimed:
        tx, ty = min(unclaimed, key=lambda p: md(sx, sy, p[0], p[1]) - 0.3 * md(ox, oy, p[0], p[1]))
    elif opp_terr:
        tx, ty = min(opp_terr, key=lambda p: md(sx, sy, p[0], p[1]) - 0.5 * md(ox, oy, p[0], p[1]))
    else:
        tx, ty = ox, oy

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = -md(nx, ny, tx, ty) + 0.15 * md(nx, ny, ox, oy)
        # Small deterministic preference for movement
        if dx == 0 and dy == 0:
            score -= 0.02
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]