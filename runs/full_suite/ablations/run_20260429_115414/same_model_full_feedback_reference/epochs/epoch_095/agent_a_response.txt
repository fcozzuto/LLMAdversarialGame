def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not legal(sx, sy):
        for dx, dy in moves:
            if legal(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if legal(x, y):
                resources.append((x, y))

    # Choose a resource that is good for us and bad for the opponent
    best = None
    best_sc = -10**9
    if resources:
        for x, y in resources:
            sd = cheb(sx, sy, x, y)
            od = cheb(ox, oy, x, y)
            # Prefer immediate wins and deny opponent; small tie-break toward closer/central
            sc = (od - sd) * 10 - sd
            sc += -((x - (W - 1) / 2) ** 2 + (y - (H - 1) / 2) ** 2) * 0.001
            if sc > best_sc:
                best_sc = sc
                best = (x, y)
    else:
        # No visible resources: go to the farthest corner from opponent deterministically
        corners = [(0, 0), (0, H - 1), (W - 1, 0), (W - 1, H - 1)]
        best = max(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))

    tx, ty = best[0], best[1]

    # Greedy one-step toward target, with opponent-avoidance if it doesn't hurt progress
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        self_prog = cheb(nx, ny, tx, ty)
        my_gain = cheb(sx, sy, tx, ty) - self_prog  # positive means closer
        opp_dist = cheb(nx, ny, ox, oy)
        # Prefer staying away when progress is similar; also avoid moving next to opponent
        sc = my_gain * 100 + opp_dist * 2
        # If we step onto/adjacent to opponent-target area, reduce slightly to avoid immediate contest
        sc -= 6 if self_prog == 0 else 0
        cand.append((sc, nx, ny, dx, dy))

    if not cand:
        return [0, 0]

    cand.sort(reverse=True)
    return [int(cand[0][3]), int(cand[0][4])]