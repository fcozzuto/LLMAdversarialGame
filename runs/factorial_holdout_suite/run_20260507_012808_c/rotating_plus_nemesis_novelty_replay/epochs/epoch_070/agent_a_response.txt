def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(a, b, c, d):
        ddx = a - c
        if ddx < 0: ddx = -ddx
        ddy = b - d
        if ddy < 0: ddy = -ddy
        return ddx + ddy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        # Target resource I can reach relatively first; if opponent is closer, bias away.
        best_val = 10**9
        best_t = resources[0]
        for rx, ry in resources:
            myd = man(rx, ry, sx, sy)
            opd = man(rx, ry, ox, oy)
            # Prefer my advantage; slight discouragement if I’m behind.
            val = myd - int(0.9 * opd)
            # Tie-break toward nearer actual distance (faster collection).
            val = val * 100 + myd
            if val < best_val:
                best_val = val
                best_t = (rx, ry)

        tx, ty = best_t
        # Intercept when opponent is already extremely close: steer toward a cell that reduces their gain
        # by heading to the target sooner (keeps pressure).
        # Move greedily one step toward target, avoiding obstacles.
        best_d = 10**9
        best_move = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = man(tx, ty, nx, ny)
                if d < best_d:
                    best_d = d
                    best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No visible resources: move to reduce distance to opponent position (to contest future spawns).
    best_d = 10**9
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            d = man(nx, ny, ox, oy)
            if d < best_d:
                best_d = d
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]