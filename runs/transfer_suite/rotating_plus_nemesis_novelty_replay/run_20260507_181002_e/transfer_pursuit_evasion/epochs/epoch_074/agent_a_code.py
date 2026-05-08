def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()

    self_is_pursuer = ("pursuer" in sr) or ("chaser" in sr) or ("seeker" in sr)
    opp_is_pursuer = ("pursuer" in orr) or ("chaser" in orr) or ("seeker" in orr)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Assume opponent deterministically chooses best move w.r.t. their role.
    def best_opp_move(ex, ey, tx, ty, opp_pursuer):
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = ex + dx, ey + dy
            if not legal(nx, ny):
                continue
            val = d2(nx, ny, tx, ty)
            # If opponent is pursuer: they minimize distance to our target; else maximize.
            val = -val if opp_pursuer else val
            if best is None or val > bestv:
                bestv, best = val, (nx, ny)
        return best if best is not None else (ex, ey)

    best_move = (0, 0)
    bestv = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Opponent response: use our candidate position as target.
        npx, npy = best_opp_move(ox, oy, nx, ny, opp_is_pursuer)

        dist = d2(npx, npy, nx, ny)
        # If we are pursuer, we want small dist after their move; if evader, large dist.
        val = -dist if self_is_pursuer else dist

        # Tie-breaker: prefer moves that also improve our immediate position relative to opponent.
        if bestv is None or val > bestv:
            bestv, best_move = val, (dx, dy)
        elif val == bestv:
            cur_improve = -d2(nx, ny, ox, oy) if self_is_pursuer else d2(nx, ny, ox, oy)
            bestx, besty = sx + best_move[0], sy + best_move[1]
            best_improve = -d2(bestx, besty, ox, oy) if self_is_pursuer else d2(bestx, besty, ox, oy)
            if cur_improve > best_improve:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]