def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    myT = set()
    for c in observation.get("self_territory") or []:
        if c and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h:
                myT.add((x, y))

    oppT = set()
    for c in observation.get("opponent_territory") or []:
        if c and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h:
                oppT.add((x, y))

    unclaimed = [(int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c and len(c) >= 2]
    if not unclaimed:
        unclaimed = [(ox, oy)]

    def min_dist_to_set(nx, ny, S):
        best = 10**9
        for (x, y) in S:
            d = abs(nx - x) + abs(ny - y)
            if d < best:
                best = d
        return best if S else 10**9

    def nearest_unclaimed_dist(nx, ny):
        best = 10**9
        for (x, y) in unclaimed:
            d = abs(nx - x) + abs(ny - y)
            if d < best:
                best = d
        return best

    best_score = -10**18
    best_move = [0, 0]
    for dx, dy, nx, ny in cand:
        d_opp = abs(nx - ox) + abs(ny - oy)
        d_my = min_dist_to_set(nx, ny, myT)
        d_un = nearest_unclaimed_dist(nx, ny)
        in_my = 1 if (nx, ny) in myT else 0
        in_opp = 1 if (nx, ny) in oppT else 0
        score = (10_000 * in_my) - (10_000 * in_opp) + (-2 * d_un) + (-1 * d_my) + (d_opp * 0.3)
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move