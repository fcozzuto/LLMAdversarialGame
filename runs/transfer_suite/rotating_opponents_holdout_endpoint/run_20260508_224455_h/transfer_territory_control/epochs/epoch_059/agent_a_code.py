def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or (0, 0)
    sx, sy = int(s[0]), int(s[1])
    o = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(o[0]), int(o[1])

    def to_set(lst):
        out = set()
        if not lst:
            return out
        for c in lst:
            try:
                x, y = int(c[0]), int(c[1])
                out.add((x, y))
            except:
                pass
        return out

    obs = to_set(observation.get("obstacles"))
    myt = to_set(observation.get("self_territory"))
    un = to_set(observation.get("unclaimed_cells"))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        score = 0
        if (nx, ny) in un:
            score += 50
        if (nx, ny) in myt:
            score += 10
        score -= abs(nx - ox) + abs(ny - oy)
        if score > best_score:
            best_score = score
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best