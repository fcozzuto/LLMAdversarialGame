def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res = [(r[0], r[1]) for r in resources if inb(r[0], r[1]) and (r[0], r[1]) not in obs]
    if not res:
        return [0, 0]

    # Predict opponent's next row step (sweep_rows behavior: first move in y toward nearest resource row).
    best_r = None
    best_key = None
    for rx, ry in res:
        key = (abs(ry - oy), abs(rx - ox))
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)
    target_ry = best_r[1]
    opp_next_y = oy + (1 if target_ry > oy else (-1 if target_ry < oy else 0))

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        move_val = -10**18
        for rx, ry in res:
            d_self = md(nx, ny, rx, ry)
            d_op = md(ox, oy, rx, ry)
            if ry == opp_next_y:
                continue  # deny likely sweep row
            margin = d_op - d_self
            val = margin * 1000 - d_self
            if val > move_val:
                move_val = val
        if move_val == -10**18:
            # Fallback: allow sweep row but strongly discourage getting stuck on it.
            for rx, ry in res:
                d_self = md(nx, ny, rx, ry)
                d_op = md(ox, oy, rx, ry)
                margin = d_op - d_self
                val = margin * 1000 - d_self - (500 if ny == opp_next_y else 0)
                if val > move_val:
                    move_val = val
        move_val -= (200 if ny == opp_next_y else 0)
        if move_val > best_val:
            best_val = move_val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]