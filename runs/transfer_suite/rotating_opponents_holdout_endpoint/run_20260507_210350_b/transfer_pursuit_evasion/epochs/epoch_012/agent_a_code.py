def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    self_role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in self_role) or ("hunter" in self_role) or ("chaser" in self_role)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Opponent likely moves too; approximate by assuming opponent keeps moving greedily w.r.t our position.
    # If we're pursuer, opponent tries to maximize distance; else opponent tries to minimize.
    opp_tries_max = not pursuer

    def opp_best_from(px, py, tx, ty):
        best = (px, py)
        bestv = -10**18 if opp_tries_max else 10**18
        for ddx, ddy in deltas:
            nx, ny = px + ddx, py + ddy
            if not inb(nx, ny):
                nx, ny = px, py
            d = cheb(nx, ny, tx, ty)
            v = d
            if opp_tries_max:
                if v > bestv or (v == bestv and (nx, ny) > best):
                    bestv, best = v, (nx, ny)
            else:
                if v < bestv or (v == bestv and (nx, ny) < best):
                    bestv, best = v, (nx, ny)
        return best[0], best[1]

    best_move = (0, 0)
    best_val = -10**18 if pursuer else 10**18
    parity = observation.get("turn_index", 0) & 1

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy

        # Estimate next opponent position given our candidate move
        nox, noy = opp_best_from(ox, oy, nx, ny)
        d_next = cheb(nox, noy, nx, ny)

        # If we're pursuer, smaller distance is better (capture at 0). If evader, larger is better.
        # Add a tiny deterministic tie-break encouraging moving to one of the main diagonals depending on parity.
        diag_pref = (nx - ny) if parity == 0 else (nx + ny)
        val = (-d_next * 1000) + diag_pref if pursuer else (d_next * 1000) + diag_pref

        if pursuer:
            if val > best_val:
                best_val, best_move = val, (dx, dy)
            elif val == best_val and (dx, dy) < best_move:
                best_move = (dx, dy)
        else:
            if val < best_val:
                best_val, best_move = val, (dx, dy)
            elif val == best_val and (dx, dy) > best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]