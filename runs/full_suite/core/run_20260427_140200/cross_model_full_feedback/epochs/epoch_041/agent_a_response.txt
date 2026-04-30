def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if resources:
        best = None
        best_val = -10**18
        for rx, ry in resources:
            d_me = man(sx, sy, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            # Prefer resources where we are significantly closer than the opponent.
            val = (d_opp - d_me) * 100 - d_me
            # Slight tie-break: prefer closer-to-center when contention is similar.
            cx, cy = (w - 1) // 2, (h - 1) // 2
            val += - (abs(rx - cx) + abs(ry - cy)) * 0.1
            if val > best_val:
                best_val = val
                best = (rx, ry)
        tx, ty = best
    else:
        # No visible resources: move toward center while keeping distance from opponent.
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_t = man(nx, ny, tx, ty)
        d_o = man(nx, ny, ox, oy)
        # Primary: reduce distance to target; Secondary: stay away from opponent.
        score = -d_t * 10 + d_o
        # If moving onto a resource, prioritize it heavily.
        if resources and (nx, ny) in set(resources):
            score += 10**6
        # Avoid cornering into obstacles by penalizing "tight" moves (few legal neighbors).
        deg = 0
        for ddx, ddy in dirs:
            ex, ey = nx + ddx, ny + ddy
            if legal(ex, ey):
                deg += 1
        score += deg * 0.2
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]