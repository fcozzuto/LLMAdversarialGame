def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((int(p[0]), int(p[1])) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Candidate destinations = 9 neighbor cells (including stay), but stay is always allowed.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (dx != 0 or dy != 0) and (not inb(nx, ny) or (nx, ny) in obstacles):
            continue

        # Evaluate by targeting a resource: prioritize those we can reach no later than opponent,
        # otherwise race for the earliest opponent arrival. Tie-break by our closeness.
        move_best = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            adv = op_d - my_d  # >0 means we arrive earlier
            if adv >= 0:
                key = (0, -adv, my_d, rx, ry)
            else:
                key = (1, op_d, my_d, rx, ry)
            if move_best is None or key < move_best:
                move_best = key

        # Prefer moves that can secure the strongest advantage; then reduce our distance.
        score = (move_best[0], move_best[1], move_best[2], move_best[3], move_best[4])
        if best is None or score < best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])] if best is not None else [0, 0]