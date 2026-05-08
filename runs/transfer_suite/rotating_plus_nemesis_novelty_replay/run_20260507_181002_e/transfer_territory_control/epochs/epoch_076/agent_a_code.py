def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    resources = toset(observation.get("resources"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            d_opp = dist(nx, ny, ox, oy)
            if resources:
                best_res = 10**9
                for rx, ry in resources:
                    if (rx, ry) not in obstacles:
                        r = dist(nx, ny, rx, ry)
                        if r < best_res:
                            best_res = r
                d_res = best_res
            else:
                d_res = 0
            score = 0
            if resources:
                score -= d_res * 2
            if d_opp <= 1:
                score -= 100
            else:
                score += d_opp
            candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    return [int(candidates[0][1]), int(candidates[0][2])]