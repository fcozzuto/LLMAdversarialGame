def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) == 2}

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best_key = None
    best = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue

        max_adv = -10**9
        min_self = 10**9
        min_opp = 10**9
        closest_resource = None

        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd
            if adv > max_adv:
                max_adv = adv
                closest_resource = (rx, ry)
            if sd < min_self:
                min_self = sd
            if od < min_opp:
                min_opp = od

        # Prefer higher immediate race advantage; then faster access for self; then deny opponent closeness.
        key = (max_adv, -min_self, min_opp)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]