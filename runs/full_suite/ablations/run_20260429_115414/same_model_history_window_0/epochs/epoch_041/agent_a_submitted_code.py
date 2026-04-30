def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obst = observation.get("obstacles") or []
    obstacles = set(obst)
    remaining = observation.get("remaining_resource_count")
    if remaining is None:
        remaining = len(resources)
    modes = (observation.get("turn_index", 0) // 4) % 2

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    target = (sx, sy)
    if resources:
        best = None
        bestv = -10**18
        for rx, ry in resources:
            ds = d2(sx, sy, rx, ry)
            do = d2(ox, oy, rx, ry)
            adv = do - ds  # positive if we are closer
            v = (1.2 * adv) + (-0.02 * ds)
            if modes == 1:
                v = (1.6 * adv) + (-0.01 * ds) + (0.0001 * (rx + ry))
            if v > bestv:
                bestv = v
                best = (rx, ry)
        target = best if best is not None else (sx, sy)

    best_move = [0, 0]
    best_score = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if dx == 0 and dy == 0:
                continue
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            if resources and target != (sx, sy):
                tdist = d2(nx, ny, target[0], target[1])
                sd = d2(nx, ny, target[0], target[1])
                od = d2(ox, oy, target[0], target[1])
                adv = od - sd
                score = (-0.01 * tdist) + (2.0 * adv)
                if modes == 1:
                    score += 0.002 * (-(nx + ny)) + (0.0001 * remaining)
            else:
                score = -d2(nx, ny, ox, oy) + 0.001 * (nx - ox)
            if score > best_score:
                best_score = score
                best_move = [dx, dy]

    return best_move