def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    for r in resources:
        if (sx, sy) == (r[0], r[1]):
            return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    best_val = -10**18

    for dxi, dyi in moves:
        nx, ny = sx + dxi, sy + dyi
        if not valid(nx, ny):
            continue

        my_row = ny == oy
        my_col = nx == ox
        val = 0
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)

            if myd == 0:
                val = 10**12 + 10**6
                break

            # Prefer resources where we are relatively closer than opponent
            rel = (opd - myd)
            # Opponent tends to sweep rows/lines: penalize targets on opponent's current row
            row_pen = 6 if ry == oy else 0
            col_pen = 2 if rx == ox else 0
            # Mild bias toward taking nearer resources first
            near_bias = -myd

            gain = rel * 120 + near_bias * 8 - row_pen - col_pen
            # If moving aligns with opponent row/col, slightly reduce benefit (avoid getting intercepted)
            if my_row or my_col:
                gain -= 3

            if gain > val:
                val = gain

        if val > best_val:
            best_val = val
            best_move = [dxi, dyi]

    return best_move