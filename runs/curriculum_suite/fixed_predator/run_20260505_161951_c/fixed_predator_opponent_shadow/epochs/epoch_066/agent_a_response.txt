def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - tx) + abs(ny - ty)
            key = (d, abs(nx - ox) + abs(ny - oy), dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1]

    def dman(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose a target resource deterministically: the one where we are closer than opponent (prefer the most).
    best_target = None
    best_target_key = None
    for rx, ry in resources:
        sd = dman(sx, sy, rx, ry)
        od = dman(ox, oy, rx, ry)
        gap = od - sd  # positive means we are closer
        # Prefer: larger gap, then smaller our distance, then deterministic position
        key = (-gap, sd, rx, ry)
        if best_target_key is None or key < best_target_key:
            best_target_key = key
            best_target = (rx, ry)

    # Evaluate moves: maximize ability to beat opponent on this (or nearby) target while still moving towards resources.
    best_move = None
    best_key = None
    rx0, ry0 = best_target
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        sd_next = dman(nx, ny, rx0, ry0)
        od_next = dman(ox, oy, rx0, ry0)
        gain = od_next - sd_next

        # Secondary: consider closest resource from the next cell for robustness
        best_sd2 = None
        for rx, ry in resources:
            sd2 = dman(nx, ny, rx, ry)
            if best_sd2 is None or sd2 < best_sd2:
                best_sd2 = sd2

        # Tiebreaks: prefer smaller our distance, then larger gain, then towards opponent to intercept slightly
        key = (-gain, best_sd2, sd_next, dman(nx, ny, ox, oy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]