def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [sx, sy]) or [sx, sy]
    obstacles = observation.get("obstacles", []) or []
    obs = set(tuple(p) for p in obstacles)

    unclaimed = observation.get("unclaimed_cells", []) or []
    unc = [tuple(p) for p in unclaimed]
    if not unc:
        # fallback: move toward opponent
        dx = (ox > sx) - (ox < sx)
        dy = (oy > sy) - (oy < sy)
        if dx != 0 or dy != 0:
            nx, ny = sx + dx, sy + dy
        else:
            nx, ny = sx, sy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            return [int(dx), int(dy)]
        return [0, 0]

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = [0, 0]
    best_key = None
    max_check = 25
    unc_sample = unc[:max_check]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d_op = abs(nx - ox) + abs(ny - oy)
        d_unc = min(abs(nx - ux) + abs(ny - uy) for (ux, uy) in unc_sample)
        on_opp = 1 if (nx, ny) == (ox, oy) else 0
        key = (-d_unc, -d_op, -on_opp, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [int(dx), int(dy)]

    return best_move