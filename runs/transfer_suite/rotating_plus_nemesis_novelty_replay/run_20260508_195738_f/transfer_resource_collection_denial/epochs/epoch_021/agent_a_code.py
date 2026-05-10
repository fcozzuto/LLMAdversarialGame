def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((int(p[0]), int(p[1])) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx = 0 if ox > sx else (w - 1 if ox < sx else sx)
        ty = 0 if oy > sy else (h - 1 if oy < sy else sy)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [int(dx), int(dy)]

    # Evaluate the best target after each candidate move; prefer moves that increase capture advantage.
    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # "Capture advantage" if we can arrive earlier; add slight preference for nearer resources.
        val = 0.0
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive means we arrive sooner
            if adv > 0:
                val += 10.0 * adv - 0.1 * sd
            elif adv == 0:
                val += 0.5 - 0.05 * sd
            else:
                val += -1.5 * (-adv) - 0.02 * sd

        # Small deterrent for getting too close to an obstacle corner case: discourage near-obstacle positions.
        near_pen = 0
        for ax, ay in obstacles_list:
            ax, ay = int(ax), int(ay)
            if abs(ax - nx) <= 1 and abs(ay - ny) <= 1:
                near_pen += 1
        val -= 0.2 * near_pen

        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        # If all moves blocked, stay.
        return [0, 0]
    return [int(best[0]), int(best[1])]