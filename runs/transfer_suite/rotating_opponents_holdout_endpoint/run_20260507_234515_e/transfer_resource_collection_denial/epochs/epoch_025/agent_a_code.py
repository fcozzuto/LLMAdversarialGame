def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def max_abs_dxdy(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = max(candidates, key=lambda t: (-max_abs_dxdy(t[2], t[3], ox, oy), -max_abs_dxdy(t[2], t[3], tx, ty)))
        return [best[0], best[1]]

    # If standing on a resource, take it.
    for r in resources:
        if r[0] == sx and r[1] == sy:
            return [0, 0]

    # Pick the target resource that we can reach before opponent (best margin),
    # breaking ties toward closer self-distance.
    def resource_key(r):
        rx, ry = r
        sd = max_abs_dxdy(sx, sy, rx, ry)
        od = max_abs_dxdy(ox, oy, rx, ry)
        return (-(od - sd), sd, rx, ry)

    resources_sorted = sorted(resources, key=resource_key)
    target = resources_sorted[0]

    tx, ty = target[0], target[1]

    # One-step lookahead: maximize advantage after the move, then proximity, then safety.
    def cell_score(nx, ny):
        sd = max_abs_dxdy(nx, ny, tx, ty)
        od = max_abs_dxdy(ox, oy, tx, ty)
        margin = od - sd  # higher means we stay ahead
        # slight preference to reduce distance to next-best resource if we can't beat hard
        best2 = -10**9
        for r in resources_sorted[:4]:
            rx, ry = r
            sd2 = max_abs_dxdy(nx, ny, rx, ry)
            od2 = max_abs_dxdy(ox, oy, rx, ry)
            val = od2 - sd2
            if val > best2:
                best2 = val
        # obstacle avoidance: count immediate free neighbors
        free = 0
        for ddx, ddy in deltas:
            px, py = nx + ddx, ny + ddy
            if inb(px, py) and (px, py) not in obstacles:
                free += 1
        return (margin * 1000 + best2, -sd, -free, nx, ny)

    best = max(candidates, key=lambda t: cell_score(t[2], t[3]))
    return [best[0], best[1]]