def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obstacles.add((ax, ay))

    self_role = (observation.get("self_role") or "").lower()
    opponent_role = (observation.get("opponent_role") or "").lower()
    # Heuristic: if we are not the pursuer, we treat ourselves as evader.
    i_am_evader = ("evader" in self_role) or ("pursuer" not in self_role and "pursuer" in opponent_role)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1,  0), (0, 0), (1,  0),
             (-1,  1), (0, 1), (1,  1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Prefer avoiding being blocked by favoring moves that preserve options.
    def dist_metric(nx, ny):
        return abs(nx - ox) + abs(ny - oy)

    best = None
    best_score = None
    prefer = -1 if i_am_evader else 1  # evader: maximize, pursuer: minimize

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist_metric(nx, ny)
        # Count immediate valid neighbors after move (deterministic tie-break helper)
        options = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if valid(tx, ty):
                options += 1

        # Also bias away from getting stuck near obstacles when evading; bias toward closing when pursuing.
        score = (prefer * d * 1000) + (options if i_am_evader else -options)
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
        elif score == best_score and best is not None:
            # deterministic lexicographic tie-break
            cand = (dx, dy)
            if cand < best:
                best = cand

    # If all moves invalid, stay still.
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]