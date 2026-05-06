def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    if not resources:
        return [0, 0]

    obst = set((p[0], p[1]) for p in obstacles)

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    best_s = -10**18

    # Heuristic: sweep_rows opponent likely contests via row-chains; align y and deny resources where opponent is ahead.
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obst:
            continue

        row_align = -abs(ny - oy)  # prefer being on opponent's row
        col_align = -abs(nx - ox) * 0.2

        s = row_align + col_align
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            if ny == ry:
                s += 14  # being on the same row as a resource is valuable vs sweep-row behavior
            rel = op_d - my_d  # positive => we are closer than opponent
            if rel > 0:
                s += rel * 60 - my_d * 6
            else:
                # if opponent is closer, contest by reducing the gap and preferring nearer-after-move
                s += -(-rel) * 18 - my_d * 2 + op_d * 1.2

        # slight preference for reducing distance to the best "target" resource overall
        best_target = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < best_target:
                best_target = d
        s += -best_target * 8

        if s > best_s:
            best_s = s
            best = [dx, dy]

    return best