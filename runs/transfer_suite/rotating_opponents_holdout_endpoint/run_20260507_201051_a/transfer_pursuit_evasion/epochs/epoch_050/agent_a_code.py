def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = observation.get("self_role", "pursuer")

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def obstacle_neighbors(nx, ny):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (nx + dx, ny + dy) in obs:
                    c += 1
        return c

    best = None
    best_val = None  # higher is better for evader, lower is better for pursuer
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)
        neigh = obstacle_neighbors(nx, ny)

        if role == "pursuer":
            # Prefer approaching; avoid getting boxed in by obstacles.
            val = d + 2.5 * neigh
        else:
            # Prefer escaping; also prefer safer cells and pushing toward far corners.
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            far_corner = max(corners, key=lambda c: dist2(c[0], c[1], nx, ny))
            corner_push = dist2(nx, ny, far_corner[0], far_corner[1])
            val = -(d + 0.7 * corner_push) + 2.0 * neigh  # larger d/corner better; penalize boxed-in

        if best is None:
            best, best_val = (dx, dy), val
        else:
            if role == "pursuer":
                if val < best_val:
                    best, best_val = (dx, dy), val
            else:
                if val < best_val:
                    best, best_val = (dx, dy), val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]