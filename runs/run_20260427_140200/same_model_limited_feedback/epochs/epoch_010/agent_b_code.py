def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((x, y) for x, y in obstacles)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def clamp_in(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    best_move = [0, 0]
    best_score = None
    best_tiebreak = None

    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not clamp_in(nx, ny) or (nx, ny) in obs_set:
                continue
            t_best = None
            t_tie = None
            for rx, ry in resources:
                sd = d2(nx, ny, rx, ry)
                od = d2(ox, oy, rx, ry)
                val = od - sd  # positive if we are closer than opponent
                # prefer winning resource; tie-break by being closer (smaller sd), then lexicographic
                if (t_best is None) or (val > t_best) or (val == t_best and (t_tie is None or sd < t_tie or (sd == t_tie and (rx, ry) < (rtx, rty)))):
                    t_best = val
                    t_tie = sd
                    rtx, rty = rx, ry
            if t_best is None:
                continue
            # overall tie-break: higher val first, then smaller distance to selected resource, then prefer moves with smaller dx, then dy for determinism
            overall = t_best
            tieb = t_tie
            if (best_score is None) or (overall > best_score) or (overall == best_score and (tieb < best_tiebreak or (tieb == best_tiebreak and (dx, dy) < tuple(best_move)))):
                best_score = overall
                best_tiebreak = tieb
                best_move = [dx, dy]
        return [int(best_move[0]), int(best_move[1])]
    else:
        # No resources: move to reduce distance to opponent (deterministic "pressure") while avoiding obstacles
        best = [0, 0]
        bestd = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not clamp_in(nx, ny) or (nx, ny) in obs_set:
                continue
            dist = d2(nx, ny, ox, oy)
            if (bestd is None) or (dist < bestd) or (dist == bestd and (dx, dy) < tuple(best)):
                bestd = dist
                best = [dx, dy]
        return [int(best[0]), int(best[1])]