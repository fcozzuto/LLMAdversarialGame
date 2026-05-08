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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_pursuer = ("pursuer" in sr) or ("chaser" in sr) or ("seeker" in sr)
    self_is_evader = not self_is_pursuer

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def best_reply(ex, ey, tx, ty, opp_is_pursuer):
        # Return value of distance after opponent moves (1-ply).
        # If opponent is pursuer: minimize distance; else maximize.
        bestv = None
        bestd = None
        for dx, dy in moves:
            nx, ny = ex + dx, ey + dy
            if not legal(nx, ny):
                continue
            d = dist2(nx, ny, tx, ty)
            v = d if not opp_is_pursuer else -d
            # deterministic tie-break: lexicographic by move and then smaller/larger d accordingly
            if bestv is None:
                bestv, bestd = v, d
            else:
                if (not opp_is_pursuer and v > bestv) or (opp_is_pursuer and v > bestv):
                    bestv, bestd = v, d
                elif v == bestv and ((d < bestd) if opp_is_pursuer else (d > bestd)):
                    bestd = d
        if bestd is None:
            return dist2(ex, ey, tx, ty)
        return bestd

    # Decide our move via 1-ply minimax/worst-case against assumed opponent policy.
    # If we're pursuer: opponent is evader (maximize distance). If we're evader: opponent pursuer (minimize distance).
    opp_is_pursuer = self_is_evader  # when we're evader, opponent is pursuer in pursuit_evasion
    best_val = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_after = best_reply(ox, oy, nx, ny, opp_is_pursuer)
        # objective: pursuer minimize opponent distance; evader maximize it
        val = d_after if self_is_evader else -d_after
        # tie-breaker: closer (pursuer) / farther (evader) to keep pressure toward corners/edges
        corner_bias = 2 * (min(nx, w - 1 - nx) + min(ny, h - 1 - ny))
        tie = (val, -corner_bias) if self_is_pursuer else (val, corner_bias)
        if best_val is None:
            best_val, best_move = tie, (dx, dy)
        else:
            if tie > best_val:
                best_val, best_move = tie, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]