def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # resource_denier: prioritize resources we can reach at least as fast as opponent,
        # otherwise contest those where opponent is close.
        my_win = sd - od
        key = (
            0 if my_win <= 0 else 1,     # prefer we are not slower
            abs(my_win),                 # then closer "race"
            sd,                          # then closer to us
            -rx, -ry                     # tie-break deterministically
        )
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cur_to = cheb(sx, sy, tx, ty)

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(nx, ny, ox, oy)

        # If the move brings us closer to target and keeps opponent farther, choose it.
        # Small deterministic tie-breaking favors advancing toward target.
        val = (
            nsd,                 # minimize distance to target
            -nod,                # maximize distance from opponent (denial)
            abs(dx) + abs(dy),  # prefer not to over-shift
            (nx - sx, ny - sy)   # deterministic
        )
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [dx, dy]