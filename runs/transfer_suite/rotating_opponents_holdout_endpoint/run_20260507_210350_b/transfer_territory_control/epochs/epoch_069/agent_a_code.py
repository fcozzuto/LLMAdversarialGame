def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    oppT = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    opp_pos = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = (None, -10**9)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in oppT:
            score = 100000 - dist(nx, ny, ox, oy)
        elif (nx, ny) in unclaimed:
            score = 5000 + 10 * (min(dist(nx, ny, ox, oy), dist(sx, sy, ox, oy)) == dist(nx, ny, ox, oy)) - dist(nx, ny, ox, oy)
        elif (nx, ny) in selfT:
            score = 500 - dist(nx, ny, ox, oy) // 2
        else:
            score = 0 - dist(nx, ny, ox, oy)
        if (dx, dy) == (0, 0):
            score -= 5
        if score > best[1]:
            best = ((dx, dy), score)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]