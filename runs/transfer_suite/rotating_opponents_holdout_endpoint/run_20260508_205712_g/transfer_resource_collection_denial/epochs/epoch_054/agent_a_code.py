def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def best_move_towards(tx, ty):
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d_to = abs(nx - tx) + abs(ny - ty)
            d_opp = abs(nx - ox) + abs(ny - oy)
            # Primary: get closer to target. Secondary: keep away from opponent.
            key = (d_to, -d_opp, nx, ny)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    # If no resources visible, head to the most distant corner from opponent (deterministic)
    if not resources:
        corners = [(0, 0), (0, H - 1), (W - 1, 0), (W - 1, H - 1)]
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
        return best_move_towards(tx, ty)

    # Race closest resource, but heavily penalize resources where opponent is already closer.
    best_key = None
    best_r = None
    for rx, ry in resources:
        my_d = abs(sx - rx) + abs(sy - ry)
        op_d = abs(ox - rx) + abs(oy - ry)
        penalty = 4 if op_d < my_d else 0
        # Deterministic tie-breaker by position
        key = (my_d + penalty, op_d - my_d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    return best_move_towards(tx, ty)