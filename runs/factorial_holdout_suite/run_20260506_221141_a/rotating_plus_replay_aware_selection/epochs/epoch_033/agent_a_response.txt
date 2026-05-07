def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Value: how much closer we are than opponent to the same resource (larger is better).
        # Tie-break: smaller self distance to secure faster collection.
        vbest = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            v = (do - ds)
            if vbest is None or v > vbest[0] or (v == vbest[0] and ds < vbest[1]):
                vbest = (v, ds)
        # Small additional preference: avoid stepping away from the currently best resource.
        if best is None or vbest[0] > best[0] or (vbest[0] == best[0] and vbest[1] < best[1]):
            best = vbest
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]