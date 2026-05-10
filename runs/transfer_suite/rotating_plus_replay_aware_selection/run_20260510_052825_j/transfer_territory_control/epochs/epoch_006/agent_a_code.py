def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    ox, oy = observation.get("opponent_position", (x, y))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**9
    opp_dist_now = abs(x - ox) + abs(y - oy)

    def score_cell(nx, ny):
        if (nx, ny) in obstacles:
            return -10**8
        s = 0
        if (nx, ny) in oppT:
            s += 50
        elif (nx, ny) in unclaimed:
            s += 35
        elif (nx, ny) in selfT:
            s += 10
        else:
            s += 5

        # Prefer progressing in the direction where we can capture more unclaimed,
        # but keep some pressure against the opponent.
        if unclaimed:
            # Deterministic local estimate: closest unclaimed distance after move.
            best_u = 10**9
            for (ux, uy) in unclaimed:
                d = abs(nx - ux) + abs(ny - uy)
                if d < best_u:
                    best_u = d
            s += max(0, 20 - best_u)

        # Tie-breakers: move that reduces opponent distance slightly; avoid giving it easy access.
        opp_dist = abs(nx - ox) + abs(ny - oy)
        s += (opp_dist_now - opp_dist) * 2

        # Avoid moving into tight "dead" areas: count available neighbors (not obstacles).
        free = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                free += 1
        s += free * 0.5
        return s

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            sc = score_cell(nx, ny)
            if sc > best_score:
                best_score = sc
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]