def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_cell(nx, ny):
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return None
        # Tactical bias: aim to intercept around the middle column early (strong vs edge patrol),
        # but still prioritize resources deterministically.
        midx = (w - 1) // 2
        midy = (h - 1) // 2
        intercept_bias = abs(nx - midx) * 0.9 + abs(ny - midy) * 0.35
        if resources:
            nearest = 10**9
            for rx, ry in resources:
                d = abs(nx - rx) + abs(ny - ry)
                if d < nearest:
                    nearest = d
            # Encourage getting closer to resources while keeping intercept bias in tie-breaks.
            return nearest * 1.0 + intercept_bias
        # No resources visible: drift towards center while avoiding edges/obstacles.
        return intercept_bias

    best = None
    best_move = [0, 0]
    # Deterministic move ordering based on score_cell; break ties by dx,dy preference.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sc = score_cell(nx, ny)
        if sc is None:
            continue
        cand = (sc, abs(dx) + abs(dy), dx, dy)
        if best is None or cand < best:
            best = cand
            best_move = [dx, dy]

    return best_move