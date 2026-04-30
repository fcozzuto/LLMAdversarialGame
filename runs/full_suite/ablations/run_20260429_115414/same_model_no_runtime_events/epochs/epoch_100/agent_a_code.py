def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Deterministic tie-breaking via move order and stable resource ordering.
    resources = sorted(set(resources))
    best_move = (0, 0)
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Prefer actions that improve our race advantage to some resource.
        # Score = (opp_distance - my_distance) with a small preference for nearer resources overall.
        local_best = -10**9
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # If we're already on a resource, strongly prefer.
            if d_me == 0:
                s = 10000 - d_opp
            else:
                s = (d_opp - d_me) * 100 - (d_me * 3 + d_opp * 1)
                # Nudge toward ending in open space (avoid stepping into tight spots).
                # Deterministic small bonus based on available neighboring cells.
                open_cnt = 0
                for adx, ady in moves:
                    tx, ty = nx + adx, ny + ady
                    if valid(tx, ty):
                        open_cnt += 1
                s += open_cnt
            if s > local_best:
                local_best = s
        if local_best > best_score:
            best_score = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]