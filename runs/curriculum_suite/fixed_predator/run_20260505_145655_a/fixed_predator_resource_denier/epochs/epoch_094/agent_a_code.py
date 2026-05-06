def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Evaluate each candidate move by best "contested" resource after moving.
    best_move = None
    for dx, dy, nx, ny in legal:
        best_val = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive if we are closer
            # Prefer resources where we can deny: be closer (adv>0) and keep opponent from being too close.
            val = adv * 30 - sd - 0.35 * od - 0.002 * (rx + ry)
            if best_val is None or val > best_val:
                best_val = val
        # Small deterministic tie-break: prefer staying closer to center of our side (reduce drifting).
        center_bias = -abs(nx - 3.5) - abs(ny - 3.5)
        val2 = best_val + 0.01 * center_bias
        if best_move is None or val2 > best_move[0] or (val2 == best_move[0] and (dx, dy) < (best_move[1], best_move[2])):
            best_move = (val2, dx, dy)

    return [best_move[1], best_move[2]]