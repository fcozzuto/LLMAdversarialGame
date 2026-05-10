def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in observation.get("obstacles") or [])
    if not resources:
        return [0, 0]

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    res = [(int(x), int(y)) for x, y in resources]
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def safe(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def step_penalty(nx, ny):
        # discourage moving next to obstacles to reduce getting stuck; deterministic local heuristic
        p = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                tx, ty = nx + ex, ny + ey
                if (tx, ty) in obstacles:
                    p += 1
        return p

    # Choose move maximizing advantage over opponent for the "most contested" reachable resource.
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue

        # If we can grab a resource this turn, heavily prioritize it.
        if (nx, ny) in obstacles:
            continue
        grabbed = 1 if (nx, ny) in set(res) else 0

        # Evaluate best resource for us while penalizing resources where opponent is closer.
        my_best = None
        for rx, ry in res:
            myd = d2(nx, ny, rx, ry)
            opd = d2(ox, oy, rx, ry)
            # Lower myd is good; higher (myd - opd) is bad. We also favor resources nearer to opponent only if we have clear edge.
            adv = myd - opd
            key = (adv, myd, rx, ry)  # deterministic
            if my_best is None or key < my_best[0]:
                my_best = (key, adv, myd)
        adv_key, adv, myd = my_best[0], my_best[1], my_best[2]

        # Score: higher is better
        score = (10000 * grabbed) - (adv * 50) - (myd) - (step_penalty(nx, ny) * 2)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            # tie-break deterministically: prefer staying or smaller dx/dy magnitude then lexicographic
            if (abs(dx) + abs(dy), dx, dy) < (abs(best_move[0]) + abs(best_move[1]), best_move[0], best_move[1]):
                best_move = [dx, dy]

    return best_move