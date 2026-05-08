def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if (nx, ny) == (sx, sy):
                continue
            if inb(nx, ny) and (nx, ny) not in obs:
                valid.append((dx, dy))
    valid.append((0, 0))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = (0, 0)
    if resources:
        best_score = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            # Score: prefer resources we can reach before opponent; small tie preference for nearer
            score = 0
            for rx, ry in resources:
                d_me = man(nx, ny, rx, ry)
                d_op = man(ox, oy, rx, ry)
                reach = d_op - d_me  # positive if we are closer
                if reach > 0:
                    gain = 50 * reach - 2 * d_me
                else:
                    gain = -10 * (-reach) - 2 * d_me
                if (rx, ry) == (nx, ny):
                    gain += 100000  # immediate pickup
                score += gain
            if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No visible resources: drift toward center while keeping distance from opponent
    tx, ty = w // 2, h // 2
    best = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        d_center = man(nx, ny, tx, ty)
        d_op = man(nx, ny, ox, oy)
        key = (d_center, -d_op, dx, dy)  # closer to center, farther from opponent
        if best is None or key < best:
            best = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]