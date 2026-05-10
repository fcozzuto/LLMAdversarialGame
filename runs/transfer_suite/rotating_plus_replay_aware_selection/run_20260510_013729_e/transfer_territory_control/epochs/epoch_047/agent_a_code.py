def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    xp, yp = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or [0, 0]
    xo, yo = int(op[0]), int(op[1])

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    myt = to_set("self_territory")
    opt = to_set("opponent_territory")

    neighbors = []
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in moves:
        nx, ny = xp + dx, yp + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            neighbors.append((dx, dy, nx, ny))

    if not neighbors:
        return [0, 0]

    dirs4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    def frontier_score(x, y):
        cnt = 0
        for ax, ay in dirs4:
            if (x + ax, y + ay) in myt:
                cnt += 1
        return cnt

    best = None
    for dx, dy, nx, ny in neighbors:
        s = 0.0

        if (nx, ny) in unclaimed:
            s += 80.0
        if (nx, ny) in myt:
            s += 12.0
        if (nx, ny) in opt:
            s -= 75.0

        s += 10.0 * frontier_score(nx, ny)  # expand from our border

        d_me = abs(nx - xp) + abs(ny - yp)
        d_op = abs(nx - xo) + abs(ny - yo)

        s += -0.35 * d_op  # keep away from opponent to reduce flips/counterclaims
        s += -0.05 * (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))  # mild center bias

        # Prefer moves that do not step into opponent territory, but still allow capture if it wins space
        if (nx, ny) in opt:
            s += -5.0 * frontier_score(nx, ny)  # discourage claiming inside their frontier

        # Tie-break deterministically: lowest dx, then lowest dy
        key = (-s, dx, dy, nx, ny)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [int(best[1]), int(best[2])]