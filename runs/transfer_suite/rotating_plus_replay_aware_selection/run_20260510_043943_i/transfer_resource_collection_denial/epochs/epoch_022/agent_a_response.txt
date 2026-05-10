def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def blocked(x, y):
        return (x, y) in obstacles

    def step_score(nx, ny):
        if not resources:
            # evade: maximize minimum distance from opponent potential next positions
            min_d = 10**9
            for odx, ody in deltas:
                tx, ty = ox + odx, oy + ody
                if inb(tx, ty) and not blocked(tx, ty):
                    d = man(nx, ny, tx, ty)
                    if d < min_d:
                        min_d = d
            return (min_d, -man(nx, ny, ox, oy))
        # resource race: maximize being closer than opponent, prefer closer overall and adjacent pickup
        best = (-10**9, 10**9)
        for rx, ry in resources:
            d1 = man(nx, ny, rx, ry)
            d2 = man(ox, oy, rx, ry)
            # if we're on a resource, huge boost
            adj_bonus = 20 if d1 == 0 else (8 if d1 == 1 else 0)
            # prefer states where we are already ahead of opponent for that resource
            ahead = (d2 - d1)
            # slight preference for moving toward nearer resources
            s = ahead * 5 + adj_bonus - d1
            key = (s, d1)
            if key > best:
                best = key
        return best

    best_mv = [0, 0]
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        key = step_score(nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_mv = [dx, dy]

    # If all blocked/unreachable, stay put deterministically
    return best_mv