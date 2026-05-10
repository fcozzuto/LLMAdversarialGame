def choose_move(observation):
    sx, sy = observation["self_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    ox, oy = (observation.get("opponent_position") or [w - 1, h - 1])
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x, y, a, b):
        dx = x - a
        if dx < 0: dx = -dx
        dy = y - b
        if dy < 0: dy = -dy
        return dx + dy

    def obstacle_penalty(x, y):
        p = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                p += 1
        return p

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        if (nx, ny) in unclaimed:
            base = 18
        elif (nx, ny) in self_terr:
            base = 6
        elif (nx, ny) in opp_terr:
            base = 9
        else:
            base = 3
        score = base
        score += 0.15 * dist(nx, ny, sx, sy)  # slight keep pressure smoothness
        score -= 0.35 * dist(nx, ny, ox, oy)  # avoid walking into opponent
        score -= 1.0 * obstacle_penalty(nx, ny)
        # tie-break deterministically: prefer lexicographically smaller (dx,dy)
        cand = (score, -abs(dx) - abs(dy), -dist(nx, ny, ox, oy), dx, dy)
        if best is None or cand > best:
            best = cand
            best_score = score

    return [best[3], best[4]]