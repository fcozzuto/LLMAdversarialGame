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

    if not resources:
        return [0, 0]

    # Select a target resource where we are relatively closer than opponent (resource denial).
    best_t = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        sd = abs(sx - rx) + abs(sy - ry)
        od = abs(ox - rx) + abs(oy - ry)
        # Primary: maximize advantage (opponent far). Secondary: minimize our distance.
        # Tertiary: deterministic position tie-break.
        key = (od - sd, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    if best_t is None:
        return [0, 0]

    rx, ry = best_t

    # Choose move maximizing immediate advantage and also progressing to the target.
    best_m = [0, 0]
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nsd = abs(nx - rx) + abs(ny - ry)
        nod = abs(ox - rx) + abs(oy - ry)
        # Immediate priority: improve our distance-to-target, and increase denial margin (od - sd).
        # Small bias to avoid getting stuck in corners by preferring any movement when equal.
        key = (-(nsd - (abs(sx - rx) + abs(sy - ry))), (nod - nsd), -nsd, dx, dy)
        if best_mkey is None or key > best_mkey:
            best_mkey = key
            best_m = [dx, dy]

    return best_m