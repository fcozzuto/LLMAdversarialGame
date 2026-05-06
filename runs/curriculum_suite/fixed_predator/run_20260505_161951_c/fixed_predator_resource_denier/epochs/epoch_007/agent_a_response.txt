def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacle_set = {(a, b) for a, b in obstacles}

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    # If no resources: maximize separation while avoiding obstacles
    if not resources:
        best = (0, 0)
        best_sep = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacle_set:
                continue
            sep = max(abs(nx - ox), abs(ny - oy))
            if sep > best_sep or (sep == best_sep and (dx, dy) < best):
                best_sep = sep
                best = (dx, dy)
        return [best[0], best[1]]

    def cheb(ax, ay, bx, by):
        da = abs(ax - bx)
        db = abs(ay - by)
        return da if da > db else db

    # Deterministic evaluation: after one move, choose best resource for denial
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacle_set:
            continue

        # Find best target from this hypothetical position
        best_t_val = -10**18
        best_t_sd = 10**9
        best_tx_ty = (10**9, 10**9)
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer stealing/denying: when we are closer, value is high; when farther, we still
            # try to reduce the gap. Penalize being far from the target.
            gap = od - sd
            val = gap * 100 - sd
            # Tie-break deterministically (smaller self distance, then lexicographic resource)
            if val > best_t_val or (val == best_t_val and (sd < best_t_sd or (sd == best_t_sd and (rx, ry) < best_tx_ty))):
                best_t_val = val
                best_t_sd = sd
                best_tx_ty = (rx, ry)

        # Slight preference for moves that progress toward the chosen best target direction
        val = best_t_val
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]