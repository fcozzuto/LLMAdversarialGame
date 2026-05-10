def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def manhattan(a, b, c, d): return abs(a - c) + abs(b - d)

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        d_op = manhattan(nx, ny, ox, oy)

        if (nx, ny) in opp_t:
            score += 10000 - d_op
        elif (nx, ny) in unclaimed:
            score += 700 - 3 * d_op
            if nx in (0, w - 1) or ny in (0, h - 1):
                score += 60
        elif (nx, ny) in self_t:
            score += 90
            if nx in (0, w - 1) or ny in (0, h - 1):
                score += 30
        else:
            score += 10

        # Mild obstacle-threat and "boundary pressure" shaping
        if (nx, ny) in unclaimed:
            adj_pen = 0
            for adx in (-1, 0, 1):
                for ady in (-1, 0, 1):
                    if adx == 0 and ady == 0:
                        continue
                    ax, ay = nx + adx, ny + ady
                    if (ax, ay) in obstacles:
                        adj_pen -= 25
            score += adj_pen

        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move