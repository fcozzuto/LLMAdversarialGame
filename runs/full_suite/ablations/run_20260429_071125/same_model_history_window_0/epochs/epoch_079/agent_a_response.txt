def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    turn = observation.get("turn_index", 0)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    # If standing on a resource, move to a nearby alternative to avoid waste.
    if resources and any(p[0] == sx and p[1] == sy for p in resources):
        candidates = [(sx + dx, sy + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                      if not (dx == 0 and dy == 0) and inb(sx + dx, sy + dy) and (sx + dx, sy + dy) not in obstacles]
        if candidates:
            resources_set = set((p[0], p[1]) for p in resources)
            for nx, ny in candidates:
                if (nx, ny) in resources_set:
                    return [nx - sx, ny - sy]

    # Choose target deterministically; alternate between nearest and "best contested" to change policy.
    if resources:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_self = dist((sx, sy), (rx, ry))
            d_opp = dist((ox, oy), (rx, ry))
            if d_self == 0:
                score = 1e9
            else:
                # Even turns: prioritize closest. Odd turns: prioritize resources we can beat/deny.
                if turn % 2 == 0:
                    score = -d_self + 0.5 * (d_opp - d_self)
                else:
                    # Higher when opponent is far and self is not too far.
                    score = (d_opp - d_self) * 4 - d_self
            if best is None or score > best[0]:
                best = (score, rx, ry)
        tx, ty = best[1], best[2]
    else:
        # No resources: drift to center and away from opponent slightly.
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Evaluate one-step moves with simple obstacle + opponent pressure.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            # Prefer staying if forced; otherwise compute heuristic.
            d_t = dist((nx, ny), (tx, ty))
            d_o = dist((nx, ny), (ox, oy))
            # If too close to opponent, add repulsion; if we can outflank to a contested point, slight preference.
            close_pen = 0
            if d_o <= 2:  # within 1 step (or diagonal-adjacent)
                close_pen = 50
            # Mild preference not to collide with opponent position exactly.
            if nx == ox and ny == oy:
                close_pen += 100
            heuristic = -d_t + (0.2 * d_o) - close_pen
            # If we're at target, prefer not to move far.
            if (tx, ty) == (nx, ny):
                heuristic += 200
            moves.append((heuristic, dx, dy))

    if not moves:
        return [0, 0]

    moves.sort(key=lambda t: (t[0], -abs(t[1]) - abs(t[2]), -t[1], -t[2]))
    return [int(moves[0][1]), int(moves[0][2])]