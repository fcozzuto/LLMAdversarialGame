def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        return [0, 0]

    # Counter sweep_rows: avoid opponent's current row whenever possible, then race on distance.
    best = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        sd = abs(sx - rx) + abs(sy - ry)
        od = abs(ox - rx) + abs(oy - ry)
        same_row = (ry == oy)
        # Prefer different row (less contest), then prefer being closer; slight tie on opponent being slower.
        key = (0 if not same_row else -1, -sd, od - sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]

    rx, ry = best

    # Move one step toward target, avoiding obstacles; if multiple, choose deterministic tie.
    best_m = None
    best_mkey = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        nd = abs(nx - rx) + abs(ny - ry)
        # Also keep us away from stepping into opponent's immediate reach.
        opp_nd = abs(nx - ox) + abs(ny - oy)
        key = (-nd, opp_nd, -nx, -ny)
        if best_mkey is None or key > best_mkey:
            best_mkey = key
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]