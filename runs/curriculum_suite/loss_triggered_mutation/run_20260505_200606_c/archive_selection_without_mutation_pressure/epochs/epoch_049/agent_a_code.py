def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    parity = observation.get("turn_index", 0) & 1

    # Pick a resource that is relatively good for us and bad for opponent (denial bias).
    best_r = None
    best_key = None
    for rx, ry in resources:
        our_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        # Prefer closer for us, but strongly prefer being farther from opponent than we are.
        denial = opp_d - 1.2 * our_d
        # Small deterministic tie-break to vary targets.
        key = (-(denial + 0.15 * ((rx + ry + parity) % 3)), our_d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    # Choose move that reduces distance to target while (lightly) increasing distance from opponent.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_away = cheb(nx, ny, ox, oy)
        # If standing on target path is blocked, prefer shortest distance anyway; tie-break deterministically.
        val = (d_to_t, -(d_away + (0.01 if (dx, dy) == (0, 0) else 0.0)), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]