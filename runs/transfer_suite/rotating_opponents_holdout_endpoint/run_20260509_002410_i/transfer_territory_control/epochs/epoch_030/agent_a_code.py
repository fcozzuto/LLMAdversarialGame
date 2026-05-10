def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def manhattan(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    center_d_s = manhattan(sx, sy, cx, cy)
    best = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0.0
        d_op = manhattan(nx, ny, ox, oy)

        # Territory value
        if (nx, ny) in opp_t:
            score += 12000.0 - 4.0 * d_op
        elif (nx, ny) in unclaimed:
            score += 900.0 - 2.5 * d_op
        elif (nx, ny) in self_t:
            score += 120.0
        else:
            score += 30.0

        # Center pressure (opponent archetype is center-claiming)
        d_center = manhattan(nx, ny, cx, cy)
        score += 250.0 - 3.0 * d_center

        # Prefer moving to reduce distance to center; avoid getting closer to opponent only if it costs us capture
        score += 18.0 * (center_d_s - d_center)

        # Mild edge preference to keep corridors and reduce opponent reach
        if nx in (0, w - 1) or ny in (0, h - 1):
            score += 25.0

        # Don't allow staying as default if a strictly better move exists
        if dx == 0 and dy == 0:
            score -= 2.0

        if score > best_score or (score == best_score and (dx, dy) < (best[0], best[1])):
            best_score = score
            best = [dx, dy]

    return best