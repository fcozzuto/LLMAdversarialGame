def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role_s = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role_s) or ("avoid" in role_s) or ("runner" in role_s) or ("flee" in role_s)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x, y):
        dx = abs(ox - x)
        dy = abs(oy - y)
        return dx if dx > dy else dy

    def corner_dist2(x, y):
        return min(x * x + y * y,
                   (x - (w - 1)) * (x - (w - 1)) + y * y,
                   x * x + (y - (h - 1)) * (y - (h - 1)),
                   (x - (w - 1)) * (x - (w - 1)) + (y - (h - 1)) * (y - (h - 1)))

    deltas = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best_val = None
    best = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        d = cheb(nx, ny)
        # Small obstacle "gravity": avoid stepping adjacent to obstacles (more for evader, less for pursuer)
        adj = 0
        for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            px, py = nx + ax, ny + ay
            if (px, py) in blocked:
                adj += 1

        # Counter wall-runner: if opponent is near a wall, prioritize moves that keep you between it and that wall.
        wall_pen = 0
        if ox <= 1: wall_pen += 2 * (abs(nx - 1))
        if ox >= w - 2: wall_pen += 2 * (abs(nx - (w - 2)))
        if oy <= 1: wall_pen += 2 * (abs(ny - 1))
        if oy >= h - 2: wall_pen += 2 * (abs(ny - (h - 2)))

        # Deterministic tie-break via lexicographic order in deltas loop
        if is_evader:
            # maximize distance; prefer corners slightly and avoid obstacles
            val = (d, corner_dist2(nx, ny) * 0.001, -adj, -wall_pen)
            better = best_val is None or val > best_val
        else:
            # minimize distance; keep pressure while avoiding obstacles
            val = (-d, -wall_pen * 0.01, -adj * 0.1, corner_dist2(nx, ny) * 0.0)
            better = best_val is None or val > best_val

        if better:
            best_val = val
            best = (dx, dy)

    dx, dy = best
    return [int(dx), int(dy)]