def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obs = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    res = observation.get("resources", []) or []
    resources = []
    for p in res:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_opp = abs(nx - ox) + abs(ny - oy)
        score = -d_opp * 3
        if resources:
            md = 10**9
            for rx, ry in resources:
                dd = abs(nx - rx) + abs(ny - ry)
                if dd < md:
                    md = dd
            score += max(0, 6 - md)
        if best is None or score > best_score:
            best = [dx, dy]
            best_score = score
    if best is None:
        return [0, 0]
    return best