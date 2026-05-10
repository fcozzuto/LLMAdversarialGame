def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = [(p[0], p[1]) for p in resources if p and len(p) >= 2]
    obs = set((p[0], p[1]) for p in obstacles if p and len(p) >= 2)

    if not res:
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

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = (0, 0)
    best_primary = -10**9
    best_secondary = 10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Primary: maximize "capture advantage" on some resource (opponent farther than us).
        adv = -10**9
        any_pos_adv = False
        nearest = 10**9
        on_res = (nx, ny) in set(res)

        for rx, ry in res:
            if (rx, ry) in obs:
                continue
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            if d_self < nearest:
                nearest = d_self
            a = d_opp - d_self
            if a > adv:
                adv = a
            if a > 0:
                any_pos_adv = True

        # If we can ensure some resource is closer than the opponent, prioritize that.
        primary = adv if any_pos_adv else -nearest
        # Secondary: if tie, prefer faster collection by staying near/landing on resources.
        secondary = nearest
        if on_res:
            secondary = -1

        if primary > best_primary or (primary == best_primary and secondary < best_secondary) or \
           (primary == best_primary and secondary == best_secondary and (dx, dy) > best_move):
            best_primary = primary
            best_secondary = secondary
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]