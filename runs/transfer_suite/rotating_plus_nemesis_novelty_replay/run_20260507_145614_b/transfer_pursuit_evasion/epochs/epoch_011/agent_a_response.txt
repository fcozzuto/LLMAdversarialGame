def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    i_am_pursuer = ("pursuer" in role) or ("pursur" in role)
    want_min_dist = i_am_pursuer

    obst = set()
    for p in observation.get("obstacles", []):
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    def best_opp_move(myx, myy, ex, ey):
        # Opponent tries to survive if evader, or capture if pursuer.
        # So if opponent is evader, they maximize distance; if opponent is pursuer, minimize.
        opp_is_pursuer = not i_am_pursuer
        opp_want_min = opp_is_pursuer
        best = None
        bestv = None
        for dx, dy in deltas:
            nx, ny = ex + dx, ey + dy
            if not legal(nx, ny):
                continue
            v = dist2(myx, myy, nx, ny)
            if opp_want_min:
                if bestv is None or v < bestv or (v == bestv and (dx, dy) < best):
                    bestv, best = v, (dx, dy)
            else:
                if bestv is None or v > bestv or (v == bestv and (dx, dy) < best):
                    bestv, best = v, (dx, dy)
        return best if best is not None else (0, 0)

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        opp_dx, opp_dy = best_opp_move(nx, ny, ox, oy)
        fx, fy = ox + opp_dx, oy + opp_dy
        # Prefer capture immediately if pursuer; if evader, avoid getting caught.
        d2 = dist2(nx, ny, fx, fy)
        score = d2 if want_min_dist else -d2
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score and (dx, dy) < best_move:
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]