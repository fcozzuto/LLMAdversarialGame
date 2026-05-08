def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("purs" in self_role) and ("evad" not in self_role)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def obs_pen(x, y):
        if (x, y) in obstacles:
            return 10_000_000
        if not obstacles:
            return 0
        best = 10**9
        for px, py in obstacles:
            d = abs(x - px) + abs(y - py)
            if d < best:
                best = d
        if best <= 0:
            return 10_000_000
        if best == 1:
            return 2000
        if best == 2:
            return 200
        if best == 3:
            return 40
        if best == 4:
            return 10
        return 0

    # Deterministic tie-break: prefer moves with smaller dx,dy lexicographically from a fixed order.
    best_val = None
    best_move = (0, 0)

    # Small deterministic waypoint to change behavior: alternate between two opposite corners.
    t = int(observation.get("turn_index", 0) or 0)
    waypoint = (w - 1, 0) if (t % 2 == 0) else (0, h - 1)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            val = -10_000_000 if pursuer else -10_000_000  # effectively disallow
            # still compute a large negative to avoid picking
        else:
            d_next = abs(nx - ox) + abs(ny - oy)
            pen = obs_pen(nx, ny)

            if pursuer:
                # Prefer capture immediately, then minimize distance; also bias toward opponent to prevent wandering.
                capture_bonus = 1_000_000 if (nx == ox and ny == oy) else 0
                val = capture_bonus - 10 * d_next - pen
                # mild correction toward waypoint to vary paths if equal
                val += -0.1 * (abs(nx - waypoint[0]) + abs(ny - waypoint[1]))
            else:
                # Prefer maximizing distance; strongly avoid capture; steer toward waypoint to break cycles.
                capture_avoid = -1_000_000 if (nx == ox and ny == oy) else 0
                val = -capture_avoid + 10 * d_next - pen
                val += -0.2 * (abs(nx - waypoint[0]) + abs(ny - waypoint[1]))

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]