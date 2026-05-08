def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Assume opponent is trying to reach the corner farthest from us.
    cx, cy = max(corners, key=lambda c: man(sx, sy, c[0], c[1]))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = (0, 0)
    best_val = -10**18

    d0 = man(sx, sy, ox, oy)
    dc0 = man(sx, sy, cx, cy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d1 = man(nx, ny, ox, oy)
        dc1 = man(nx, ny, cx, cy)

        # Corner-runner cutoff: go for the next step that reduces corner distance and pressures opponent.
        tx = 0 if cx == nx else (1 if cx > nx else -1)
        ty = 0 if cy == ny else (1 if cy > ny else -1)
        align = (dx * tx + dy * ty)  # prefers moving in corner direction

        # Obstacle pressure: prefer staying away from obstacles adjacent to the candidate.
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if (xx, yy) in obstacles:
                    adj_pen += 1

        # Higher is better: primarily reduce distance to opponent, secondarily reduce distance to corner, keep aligned.
        val = (-1000 * d1) + (-8 * dc1) + (10 * align) + (-2 * adj_pen)

        # Small bias to not lose ground when ties occur
        if d1 == d0:
            val += (0.1 * (-dc1))
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]