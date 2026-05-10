def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose best resource by deterministic utility.
    if resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        best_u = None
        for rx, ry in resources:
            self_d = man(sx, sy, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            center_b = 0.02 * (abs(rx - cx) + abs(ry - cy))
            # Large weight on getting "more exclusive" access than opponent.
            u = (opp_d - self_d) * 100.0 - self_d - center_b
            if best is None or u > best_u or (u == best_u and (rx, ry) < best):
                best_u = u
                best = (rx, ry)
        tx, ty = best
    else:
        # If no resources, head to the opposite corner from opponent.
        tx = 0 if ox > (w - 1) / 2 else (w - 1)
        ty = 0 if oy > (h - 1) / 2 else (h - 1)

    # Evaluate immediate move options toward chosen target while keeping opponent behind.
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    dirs.append((0, 0))
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        self_d = man(nx, ny, tx, ty)
        opp_d = man(ox, oy, tx, ty)
        target_progress = -self_d
        # Prefer moves that reduce our distance and keep opponent from being closer.
        val = (opp_d - self_d) * 100.0 + target_progress
        # Small tie-break: prefer staying closer to the board center.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        val -= 0.01 * (abs(nx - cx) + abs(ny - cy))
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]