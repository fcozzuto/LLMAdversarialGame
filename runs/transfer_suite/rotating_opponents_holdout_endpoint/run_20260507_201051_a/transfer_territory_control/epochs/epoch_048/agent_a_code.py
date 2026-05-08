def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    if not unclaimed:
        for dx, dy in dirs:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    def best_dist(x, y):
        best = 10**9
        for cx, cy in unclaimed:
            d = abs(cx - x) + abs(cy - y)
            if d < best:
                best = d
                if best == 0:
                    break
        return best

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        score = 0
        if (nx, ny) in opp_t:
            score -= 500
        if (nx, ny) in unclaimed:
            score += 1000
        score -= 3 * best_dist(nx, ny)
        if (nx, ny) == (sx, sy):
            score -= 1
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]