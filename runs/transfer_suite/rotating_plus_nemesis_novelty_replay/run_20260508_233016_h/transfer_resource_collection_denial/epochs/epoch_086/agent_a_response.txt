def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = {tuple(p) for p in (observation.get("obstacles", []) or [])}
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def safety_pen(nx, ny):
        # small penalty for being adjacent to obstacles to reduce collisions
        p = 0
        for ax, ay in obstacles:
            if max(abs(ax - nx), abs(ay - ny)) == 1:
                p += 2
        return p

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate this move by best resource advantage from the next position
        # Prefer wins (my_d_next <= op_d), otherwise reduce being slower.
        my_next_best = None
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            slack = op_d - my_d
            # Winning resource: large positive, tie-break by smaller my_d then nearer to lexicographic stability.
            win_key = (1 if my_d <= op_d else 0, slack, -my_d, -abs(rx - ox), -abs(ry - oy), rx, ry)
            if my_next_best is None or win_key > my_next_best:
                my_next_best = win_key

        # Combine: maximize win_key, then discourage obstacle proximity
        val = (my_next_best, -safety_pen(nx, ny), -cheb(nx, ny, ox, oy))
        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [best[0], best[1]]