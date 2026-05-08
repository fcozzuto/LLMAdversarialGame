def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    op = observation.get("opponent_position") or None
    ox, oy = op if op else (sx, sy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    opp_t = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            opp_t.add((p[0], p[1]))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            unclaimed.append((p[0], p[1]))

    if not unclaimed and not opp_t:
        return [0, 0]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj8(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1])) == 1

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    target = None
    best = None

    if unclaimed:
        sample = unclaimed[:40]
        for c in sample:
            pr = 10**9
            if opp_t and any(adj8(c, o) for o in opp_t):
                pr = 0
            else:
                pr = dist(c, (ox, oy))
            val = (pr, dist(c, (sx, sy)), c[0], c[1])
            if best is None or val < best:
                best = val
                target = c

    if target is None and opp_t:
        # steer toward closest opponent territory cell
        closest = None
        bestd = None
        for o in list(opp_t)[:60]:
            d = dist((sx, sy), o)
            if bestd is None or d < bestd or (d == bestd and o < closest):
                bestd = d
                closest = o
        target = closest if closest else (sx, sy)

    if target is None:
        return [0, 0]

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        score = (dist((nx, ny), target), abs(dx) + abs(dy), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]