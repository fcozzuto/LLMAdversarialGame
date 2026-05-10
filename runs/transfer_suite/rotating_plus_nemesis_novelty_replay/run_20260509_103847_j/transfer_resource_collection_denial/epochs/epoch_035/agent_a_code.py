def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def step_towards(tx, ty):
        best = (0, 0)
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_self = man(nx, ny, tx, ty)
            d_opp = man(ox, oy, tx, ty)
            # Prefer decreasing our distance; tie-break by keeping opponent farther
            key = (d_self, d_opp - d_self, abs(nx - tx) + abs(ny - ty) - abs(sx - tx) - abs(sy - ty), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return best

    # Target selection: prioritize resources we are at least as close to as opponent; else pick best “near-steal”.
    best_target = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # If we can beat them soon, allow it; otherwise strongly prefer being closer now.
        can_beat_soon = 1 if sd <= od else 0
        key = (
            0 if sd <= od else 1,                # being closer is primary
            sd if sd <= od else od,            # then smaller distance
            (od - sd) if sd <= od else (sd - od),  # smaller gap
            -can_beat_soon,                   # prefer can_beat_soon
            rx, ry
        )
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    dx, dy = step_towards(tx, ty)

    # If the chosen move would step onto opponent, try an alternative best safe step (deterministic).
    nx, ny = sx + dx, sy + dy
    if (nx, ny) == (ox, oy):
        # Choose best move among safe ones that does not land on opponent.
        alt = (0, 0)
        alt_key = None
        for adx, ady in moves:
            nnx, nny = sx + adx, sy + ady
            if not valid(nnx, nny) or (nnx, nny) == (ox, oy):
                continue
            d_self = man(nnx, nny, tx, ty)
            d_opp = man(ox, oy, tx, ty)
            key = (d_self, -(d_opp - d_self), adx, ady)
            if alt_key is None or key < alt_key:
                alt_key = key
                alt = (adx, ady)
        dx, dy = alt

    return [int(dx), int(dy)]