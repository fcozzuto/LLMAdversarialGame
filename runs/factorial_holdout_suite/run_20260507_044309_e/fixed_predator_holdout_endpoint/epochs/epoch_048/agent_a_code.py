def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set((p[0], p[1]) for p in obstacles)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue

        # Look for the resource we can most "out-race" the opponent on from our next position.
        # Advantage: opponent distance minus our distance (larger is better).
        cur_best_adv = None
        cur_best_self = None
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            adv = opp_d - self_d
            if (cur_best_adv is None or adv > cur_best_adv or
                (adv == cur_best_adv and (cur_best_self is None or self_d < cur_best_self))):
                cur_best_adv = adv
                cur_best_self = self_d

        # If all resources tie strangely, prefer staying closer to the best resource.
        cand = (cur_best_adv, -cur_best_self if cur_best_self is not None else 0, -abs(ox - nx) - abs(oy - ny))
        if best is None or cand > best:
            best = cand
            best_move = [dx, dy]

    return best_move