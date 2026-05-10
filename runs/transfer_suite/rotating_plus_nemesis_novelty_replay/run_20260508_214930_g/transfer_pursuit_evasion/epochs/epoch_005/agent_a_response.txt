def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    self_role = observation.get("self_role", "")

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    obs_set = set((int(bx), int(by)) for bx, by in obstacles if isinstance(bx, (int, float)) and isinstance(by, (int, float)))

    def blocked(x, y):
        return (x, y) in obs_set

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def near_obstacle_penalty(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if blocked(x + dx, y + dy):
                    p += 1
        return p

    steps = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def resource_attracted(nx, ny):
        if not resources:
            return 0.0
        best = None
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = int(r[0]), int(r[1])
                if in_bounds(rx, ry) and not blocked(rx, ry):
                    d = dist2(nx, ny, rx, ry)
                    best = d if best is None or d < best else best
        if best is None:
            return 0.0
        return 1.0 / (1.0 + best)

    # Determine role: default assume pursuer if unknown
    is_evader = (str(self_role).lower() == "evader") or ("evader" in str(self_role).lower())

    best_move = (0, 0)
    best_val = None

    for dx, dy in steps:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)
        edge = (0 if 1 <= nx <= w - 2 else 1) + (0 if 1 <= ny <= h - 2 else 1)
        nop = near_obstacle_penalty(nx, ny)
        resv = resource_attracted(nx, ny)

        # Prefer meaningful, deterministic tradeoffs:
        if is_evader:
            # Maximize separation; if opponent is adjacent, avoid "direct closing" by penalizing moves that reduce both coordinates' sign-change
            direct = 0
            if ox != sx:
                direct += 1 if (nx - sx) * (ox - sx) > 0 else 0
            if oy != sy:
                direct += 1 if (ny - sy) * (oy - sy) > 0 else 0
            val = (d * 1.0) - (edge * 2.0) - (nop * 0.7) - (direct * 0.8) + (resv * 0.2)
        else:
            # Pursuer: minimize distance; also prefer moves that keep away from obstacles' immediate neighborhood
            val = (-d * 1.0) - (nop * 0.25) + (resv * 0.05)

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            # Deterministic tie-break: smallest lexicographic (dx, dy) but deterministic ordering by given steps
            pass

    return [int(best_move[0]), int(best_move[1])]