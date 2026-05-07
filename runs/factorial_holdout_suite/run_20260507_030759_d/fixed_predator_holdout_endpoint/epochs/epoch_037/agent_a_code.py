def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    target = None
    if resources:
        best = None
        for rx, ry in resources:
            d = abs(rx - sx) + abs(ry - sy)
            if best is None or d < best[0] or (d == best[0] and (rx, ry) < best[1]):
                best = (d, (rx, ry))
        target = best[1]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if target is not None:
            val = - (abs(target[0] - nx) + abs(target[1] - ny))
        else:
            cx, cy = w // 2, h // 2
            val = - (abs(cx - nx) + abs(cy - ny))
        if (nx, ny) != (sx, sy):
            val += 0.01  # deterministic tiny preference to move if equally good
        # Prefer staying away from opponent to reduce interference
        val -= 0.001 * (abs(ox - nx) + abs(oy - ny))
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]