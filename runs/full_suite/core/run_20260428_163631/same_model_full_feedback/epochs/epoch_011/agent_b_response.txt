def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1,  0), (0,  0), (1,  0),
            (-1,  1), (0,  1), (1,  1)]

    def md(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    # If currently on obstacle (shouldn't happen), step to best safe neighbor deterministically.
    if not safe(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if safe(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18

    # Heuristic: choose move that maximizes our chance to reach a resource first,
    # plus a mild repulsion from opponent and obstacle adjacency.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue

        # Obstacle adjacency penalty (discourage hugging obstacles).
        adj_pen = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                if (nx + ex, ny + ey) in obstacles:
                    adj_pen += 0.25

        if resources:
            # Target best resource under "we should be closer than opponent"
            best_res_val = -10**18
            for rx, ry in resources:
                d_me = md(nx, ny, rx, ry)
                d_op = md(ox, oy, rx, ry)
                # Prefer resources where we are closer; also prefer shorter absolute distance.
                v = (d_op - d_me) * 2.0 - d_me * 0.35
                if v > best_res_val:
                    best_res_val = v
            opp_repulse = md(nx, ny, ox, oy) * 0.05
            val = best_res_val + opp_repulse - adj_pen
        else:
            # No visible resources: move toward the center while keeping distance from opponent.
            cx, cy = (w - 1) // 2, (h - 1) // 2
            val = md(nx, ny, cx, cy) * -0.6 + md(nx, ny, ox, oy) * 0.25 - adj_pen

        # Deterministic tie-break: fixed order by dirs list and strict > only.
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]