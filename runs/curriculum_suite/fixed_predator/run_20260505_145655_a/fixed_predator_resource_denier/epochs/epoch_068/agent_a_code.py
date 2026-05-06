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

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_move = [0, 0]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue

            move_score = -10**18
            for rx, ry in resources:
                sd = man(nx, ny, rx, ry)
                od = man(ox, oy, rx, ry)
                center_bias = -(((rx - cx) ** 2 + (ry - cy) ** 2) * 1e-4)
                val = (od - sd) * 12 - sd * 0.8 + center_bias
                if val > move_score:
                    move_score = val

            # small preference for moving closer to opponent when denying is similar
            tie = -man(nx, ny, ox, oy) * 0.01 + -man(nx, ny, sx, sy) * 0.001
            total = move_score + tie
            if best is None or total > best:
                best = total
                best_move = [dx, dy]

    return best_move