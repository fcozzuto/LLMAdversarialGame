def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        # No resources: try to move away from opponent slightly.
        best = -10**18
        best_mv = (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = man(nx, ny, ox, oy)
            v = d
            if v > best:
                best = v
                best_mv = (dx, dy)
        return [best_mv[0], best_mv[1]]

    best = -10**18
    best_mv = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v = 0
        for rx, ry in resources:
            d_me = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            v += (d_opp - d_me) * 120 - d_me * 3
            if d_me == 0:
                v += 10**7
            elif d_me == 1:
                v += 5000
        # Prefer moves that don't let opponent win immediately on the same resource.
        for rx, ry in resources:
            if man(nx, ny, rx, ry) == 1 and man(ox, oy, rx, ry) == 0:
                v -= 10**6
                break
        if v > best:
            best = v
            best_mv = (dx, dy)

    if best_mv == (0, 0) and not valid(sx, sy):
        return [0, 0]
    return [best_mv[0], best_mv[1]]