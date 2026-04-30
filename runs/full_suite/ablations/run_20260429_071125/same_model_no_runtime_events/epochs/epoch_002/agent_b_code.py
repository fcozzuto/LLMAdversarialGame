def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        da = abs(ax - bx)
        db = abs(ay - by)
        return da if da >= db else db

    if not resources:
        best = (0, 0)
        bestv = -10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    v = -cheb((nx, ny), (ox, oy))
                    if v > bestv or (v == bestv and (dx, dy) < best):
                        bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Contest resources where we can gain the tempo; also give extra weight to resources
    # the opponent is closer to (we should try to steal/deny).
    def resource_value(me_pos):
        best = -10**18
        dm = cheb(me_pos, (ox, oy))
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_my = cheb(me_pos, (rx, ry))
            d_op = cheb((ox, oy), (rx, ry))
            # Prefer: smaller d_my, larger (d_op - d_my), and deny resources close to opponent.
            v = (d_op - d_my) * 50 - d_my * 3 - max(0, 4 - (d_op - d_my)) * 10
            # Mild tie bias for nearer resources to us.
            v += -dm * 0.01
            if v > best:
                best = v
        return best

    # Evaluate each move by resulting position; deterministic tie-break by lexicographic delta.
    best_move = None
    best_score = -10**18
    for dx, dy, nx, ny in moves:
        score = resource_value((nx, ny))
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1]) if best_move else True):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]