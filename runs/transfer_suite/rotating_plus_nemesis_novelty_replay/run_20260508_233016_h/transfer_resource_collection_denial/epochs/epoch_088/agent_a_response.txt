def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = {tuple(p) for p in (observation.get("obstacles") or [])}
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    # Opponent denier: maximize how much closer/we can beat the opponent to some resource next.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_best = None
        # Extra bias: prefer resources nearer to opponent when we can't beat them (intercept).
        for rx, ry in resources:
            my_d = dist(nx, ny, rx, ry)
            op_d = dist(ox, oy, rx, ry)
            slack = op_d - my_d  # positive means we are faster
            # If we can't be faster, we still try to reduce opponent's advantage and get close.
            val = slack * 1000 - my_d
            if my_best is None or val > my_best:
                my_best = val
        # Tie-break deterministically: prefer moves closer to opponent so we deny.
        tie = dist(nx, ny, ox, oy)
        key = (-(my_best if my_best is not None else -10**9), tie, nx, ny)
        if best_val is None or key < best_val:
            best_val = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]