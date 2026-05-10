def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = {tuple(p) for p in obs_list}

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    # Counter sweep_rows: bias toward resources that are "misaligned" with opponent
    # (so their row-bias movement is less likely to help them take the same targets).
    best = None
    best_key = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        slack = op_d - my_d  # positive => we are closer
        row_mis = 0 if ry == oy else 1
        col_mis = 0 if rx == ox else 1
        align_pen = 0.35 * (1 if (ry == oy or rx == ox) else 0)
        # Prefer: clear capture advantage, then closeness, then misalignment.
        key = (-(slack + 0.6 * row_mis + 0.6 * col_mis - align_pen), my_d, abs(rx - sx) + abs(ry - sy), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_now = cheb(sx, sy, tx, ty)
        my_next = cheb(nx, ny, tx, ty)
        op_now = cheb(ox, oy, tx, ty)
        # Approximate opponent pressure by assuming they can reduce Chebyshev distance by ~1 unless blocked.
        op_next = max(0, op_now - 1)
        # Value: maximize progress and relative advantage.
        rel_now = op_now - my_now
        rel_next = op_next - my_next
        val = (rel_next, my_next, -(abs(nx - ox) + abs(ny - oy)), -abs(nx - tx) - abs(ny - ty))
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    # If all candidate cells were invalid, stay (engine will keep us in place).
    return best_move if best_val is not None else [0, 0]