def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    res = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = p[0], p[1]
            if (rx, ry) not in obstacles:
                res.append((rx, ry))

    if not res:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    opp_adj = man(sx, sy, ox, oy) <= 2
    nearest_opp_resource = None
    nearest_opp_dist = 10**9
    if opp_adj:
        for rx, ry in res:
            d = man(ox, oy, rx, ry)
            if d < nearest_opp_dist:
                nearest_opp_dist = d
                nearest_opp_resource = (rx, ry)

    best_dx, best_dy = 0, 0
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        v = 0
        for rx, ry in res:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer
            # Contest opponent if we are behind, but strongly reward when ahead.
            if adv >= 0:
                v += adv * 250 - ds
            else:
                v += adv * 80 - ds * 3 + do * 2

            if ds == 0:
                v += 10**7

        # If opponent is pressuring, bias towards the resource they are closest to.
        if nearest_opp_resource is not None:
            rx, ry = nearest_opp_resource
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            v += (do - ds) * 400 - ds * 2
            if ds == 0:
                v += 10**8

        # Small tie-break: prefer moving away from obstacles is already handled; add prefer towards center
        v += -(abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)) * 0.01

        if v > best_val:
            best_val = v
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]