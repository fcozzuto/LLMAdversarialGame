def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(a, b, c, d): 
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy  # squared distance
    # Choose target resource: prefer ones we are closer to than opponent
    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # If we are closer, (od - sd) is positive; small tiebreak by our distance
        key = (od - sd, -sd)
        if best is None or key > best_key:
            best = (rx, ry)
            best_key = key
    # If no resources, move to a corner opposite the opponent to gain time
    if best is None:
        tx, ty = (0, h - 1) if (ox < w // 2) else (w - 1, 0)
    else:
        tx, ty = best
    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            # Evaluate move toward target and away from opponent
            d_to_target = cheb(nx, ny, tx, ty)
            d_from_opp = cheb(nx, ny, ox, oy)
            # Deterministic small bias to vary strategy by epoch parity
            parity_bias = 1 if ((observation["turn_index"] + nx + 31 * ny) & 1) == 0 else 0
            # Maximize: prefer smaller d_to_target, larger d_from_opp
            score = (-d_to_target) + (0.001 * d_from_opp) + (0.0001 * parity_bias)
            cand.append((score, dx, dy, d_to_target, -d_from_opp))
    if not cand:
        return [0, 0]
    cand.sort(reverse=True)
    return [int(cand[0][1]), int(cand[0][2])]