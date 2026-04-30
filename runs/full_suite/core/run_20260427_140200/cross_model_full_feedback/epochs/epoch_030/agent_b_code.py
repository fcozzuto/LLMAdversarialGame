def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1,  0), (0,  0), (1,  0),
            (-1,  1), (0,  1), (1,  1)]

    def dist_cheb(ax, ay, bx, by):
        return max(abs(ax - bx), abs(ay - by))

    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    best_move = [0, 0]
    best_score = -10**9

    opp_x, opp_y = ox, oy
    for dx, dy, nx, ny in cand:
        score = 0
        if (nx, ny) in resources:
            score += 10000
        if (nx, ny) == (opp_x, opp_y):
            score += 500  # reward moving toward opponent if aligned to steal later
        # moved Chebyshev distance to nearest resource
        if resources:
            d = min(dist_cheb(nx, ny, rx, ry) for rx, ry in resources)
            score -= d * 2
        # discourage staying in place when not necessary
        if dx == 0 and dy == 0:
            score -= 1

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move