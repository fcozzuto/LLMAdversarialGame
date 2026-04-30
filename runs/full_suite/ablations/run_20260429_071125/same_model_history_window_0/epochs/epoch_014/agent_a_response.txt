def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                valid.append((dx, dy, nx, ny))

    def cheb(a, b, c, d):
        return max(abs(a - c), abs(b - d))

    # Choose target resource based on distance advantage over opponent.
    best_res = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources where we are closer; if tied, prefer fewer absolute times.
        key = (myd - opd, myd, -rx, -ry, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    # If no resources, drift toward center while avoiding opponent.
    if best_res is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best_res

    # Choose move that best reduces distance to target, with opponent separation as tiebreaker.
    best_move = None
    best_score = None
    for dx, dy, nx, ny in valid:
        d_to_t = cheb(nx, ny, tx, ty)
        d_from_opp = cheb(nx, ny, ox, oy)
        # Also add slight bias toward moving (prefer progress) to avoid being stuck.
        progress = abs(nx - sx) + abs(ny - sy)
        score = (d_to_t, -d_from_opp, -progress, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]