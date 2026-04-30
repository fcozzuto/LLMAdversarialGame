def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obs = observation.get("obstacles") or []
    obstacles = set()
    for p in obs:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = observation.get("resources") or []
    resources = []
    for r in res:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(nx, ny):
        return in_bounds(nx, ny) and (nx, ny) not in obstacles

    def manh(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = [0,0]
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not safe(nx, ny):
            continue
        d_opp = manh((nx, ny), (ox, oy))
        if resources:
            d_res = min(manh((nx, ny), r) for r in resources)
            score = -d_res*8 - d_opp
        else:
            score = -d_opp
        score += 0  # deterministic baseline
        if score > best_score or (score == best_score and (nx, ny) < (mx + best[0], my + best[1])):
            best_score = score
            best = [dx, dy]

    return best