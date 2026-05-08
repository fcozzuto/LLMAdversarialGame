def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    opp_pos = observation.get("opponent_position", (sx, sy))
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_opp = dist(nx, ny, ox, oy)
        score = 0
        if (nx, ny) in opp_t:
            score += 2000
        if (nx, ny) in unclaimed:
            score += 800
        if (nx, ny) in self_t:
            score += 200
        score += 5 * (w + h - d_opp)
        if d_opp <= 1 and (nx, ny) not in opp_t and (nx, ny) not in unclaimed:
            score -= 500
        if (dx, dy) == (0, 0):
            score -= 20
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]