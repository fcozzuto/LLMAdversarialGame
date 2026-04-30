def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set((p[0], p[1]) for p in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    # Pre-filter targets to avoid obviously illegal ones
    targets = []
    for r in resources:
        rx, ry = r[0], r[1]
        if legal(rx, ry):
            targets.append((rx, ry))
    if not targets:
        # No legal resources: move to a corner-escaping diagonal toward center
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 1 if tx > sx else (-1 if tx < sx else 0)
        dy = 1 if ty > sy else (-1 if ty < sy else 0)
        return [dx, dy]

    best_move = (0, 0)
    best_score = None

    # Evaluate each move by how much it improves our advantage to the best resource
    for dx0, dy0 in moves:
        nx, ny = sx + dx0, sy + dy0
        if not legal(nx, ny):
            continue

        # One-step safety: avoid moves that immediately reduce our reachability to open cells
        # (keep local deterministic obstacle handling without full search)
        # Count legal neighbors from next position
        neigh_open = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                if legal(nx + adx, ny + ady):
                    neigh_open += 1

        my_best = None
        for rx, ry in targets:
            myd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer winning resources (opponent further), then earlier arrival, then Manhattan-ish bias
            margin = od - myd
            # Slightly prefer resources not "behind" obstacles from our next cell by using diagonal distance to origin direction
            bend = abs((rx + ry) - (nx + ny))
            key = (margin, -myd, -neigh_open, -bend, -rx, -ry)
            if my_best is None or key > my_best:
                my_best = key

        score = my_best
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx0, dy0)

    return [best_move[0], best_move[1]]