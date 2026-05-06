def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    # Prefer moves that secure a contested resource: maximize (opp_dist^2 - self_dist^2),
    # with tie-break toward smaller self distance and then toward reducing opponent advantage.
    best = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        best_val = None
        best_sdist = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # larger is better: opp farther (od) than us (sd)
            val = od - sd
            if best_val is None or val > best_val or (val == best_val and (best_sdist is None or sd < best_sdist)):
                best_val = val
                best_sdist = sd
        # secondary preference: move that improves our ability next (smaller best_sdist)
        cand = (best_val, -best_sdist)
        if best is None or cand > best:
            best = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]