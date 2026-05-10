def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles}

    def clamp_inb(x, y):
        return 0 <= x < W and 0 <= y < H

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx = 0 if ox > sx else W - 1
        ty = 0 if oy > sy else H - 1
        best = (10**9, 10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not clamp_inb(nx, ny) or (nx, ny) in obs:
                continue
            md = abs(nx - tx) + abs(ny - ty)
            if (md, abs(nx - ox) + abs(ny - oy), dx, dy) < best:
                best = (md, abs(nx - ox) + abs(ny - oy), dx, dy)
        return [best[2], best[3]]

    best_r = None
    best_key = None
    for rx, ry in resources:
        sd = abs(sx - rx) + abs(sy - ry)
        od = abs(ox - rx) + abs(oy - ry)
        # Prefer resources where we have the advantage; if tied, prefer closer ones; deterministic tie-break by coords
        key = (od - sd, -sd, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)
    tx, ty = best_r

    # Move one step toward (tx,ty), but if blocked, choose best available move by (reduce our distance, also reduce opponent's advantage)
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp_inb(nx, ny) or (nx, ny) in obs:
            continue
        sd2 = abs(nx - tx) + abs(ny - ty)
        od2 = abs(ox - tx) + abs(oy - ty)
        # Compare immediate disadvantage after move: lower is better; include opponent distance to our chosen target to avoid giving them an easy capture
        score = (sd2, (od2 - sd2), dx, dy)
        if best is None or score < best:
            best = score
    if best is None:
        return [0, 0]
    return [best[2], best[3]]