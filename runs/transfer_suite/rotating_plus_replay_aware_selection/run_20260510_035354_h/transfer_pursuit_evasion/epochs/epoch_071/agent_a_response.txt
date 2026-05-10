def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tx, ty = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    op_corner_dist = abs(ox - tx) + abs(oy - ty)
    best = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_opp_dist = abs(nx - ox) + abs(ny - oy)
        my_corner_dist = abs(nx - tx) + abs(ny - ty)
        next_op_corner_dist = op_corner_dist  # opponent position unchanged

        # Primary: trap toward their nearest corner (get closer than they are and keep narrowing gap)
        corner_gap = my_corner_dist - next_op_corner_dist  # lower is better (more containment)
        # Secondary: chase to reduce separation but avoid breaking containment too much
        key = (corner_gap, my_opp_dist, my_corner_dist, nx, ny)

        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]