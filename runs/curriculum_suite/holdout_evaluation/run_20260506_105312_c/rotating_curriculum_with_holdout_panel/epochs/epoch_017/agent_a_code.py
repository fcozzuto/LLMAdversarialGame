def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_val = -10**18

    # Counter sweep_rows: discourage grabbing resources on/near opponent row.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        move_val = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)

            # Lead term: prefer resources we can reach earlier than opponent
            lead = opd - myd
            if lead < -1:
                continue

            # Greedy improvement + anti-contestion with opponent's likely sweep row
            row_pen = 0
            if ry == oy:
                row_pen = 6
            elif abs(ry - oy) == 1:
                row_pen = 2

            # Also avoid pushing into "far" areas if opponent is close there
            dist_pen = (myd * 1) + (0 if opd >= myd else (myd - opd) * 3)

            val = lead * 12 - dist_pen - row_pen
            if val > move_val:
                move_val = val

        if move_val > best_val:
            best_val = move_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]