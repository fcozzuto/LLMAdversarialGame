def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = observation.get("self_role", "pursuer")
    opp_role = observation.get("opponent_role", "evader")
    self_is_pursuer = (self_role == "pursuer")
    opp_is_pursuer = (opp_role == "pursuer")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def edge_pen(x, y):
        return min(x, w - 1 - x) + min(y, h - 1 - y)

    def opp_best_move(npx, npy, ex, ey):
        # Opponent chooses greedily: pursuer->min distance, evader->max distance
        best = None
        bestv = None
        for dx, dy in moves:
            tx, ty = npx + dx, npy + dy
            if not legal(tx, ty):
                continue
            val = d2(tx, ty, ex, ey)
            if opp_is_pursuer:
                # Prefer closer; tie-break keep more central (smaller edge_pen) for pursuer to avoid dead-ends
                val2 = (val, edge_pen(tx, ty))
                if bestv is None or val2 < bestv:
                    bestv, best = val2, (dx, dy)
            else:
                # Prefer farther; tie-break keep more central
                val2 = (-val, edge_pen(tx, ty))
                if bestv is None or val2 < bestv:
                    bestv, best = val2, (dx, dy)
        return best if best is not None else (0, 0)

    best_move = (0, 0)
    if self_is_pursuer:
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            odx, ody = opp_best_move(ox, oy, nx, ny)
            n_ox, n_oy = ox + odx, oy + ody
            dist = d2(nx, ny, n_ox, n_oy)
            # Capture occurs when dist==0 (radius 0)
            # Score: minimize distance; tie-break prefer moves that reduce centrality around evader
            score = (dist, -edge_pen(n_ox, n_oy), dx, dy)
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
    else:
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            odx, ody = opp_best_move(ox, oy, nx, ny)
            n_ox, n_oy = ox + odx, oy + ody
            dist = d2(nx, ny, n_ox, n_oy)
            # Score: maximize distance from pursuer after its response; tie-break prefer central evasion
            score = (-dist, edge_pen(nx, ny), dx, dy)
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]