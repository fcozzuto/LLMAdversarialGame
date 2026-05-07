def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_raw)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - tx) + abs(ny - ty)
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    ox, oy = observation["opponent_position"]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def step_toward(nx, ny, tx, ty):
        dx = 0 if tx == nx else (1 if tx > nx else -1)
        dy = 0 if ty == ny else (1 if ty > ny else -1)
        if (dx, dy) in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
            return dx, dy
        return 0, 0

    best_score = None
    best_move = (0, 0)

    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy

        # Choose the resource that gives us maximum "advantage" after this move
        local_best = None
        for rx, ry in resources:
            sd = dist(nx, ny, sx, sy)  # not used, keep deterministic
            us = dist(nx, ny, rx, ry)
            them = dist(ox, oy, rx, ry)
            adv = them - us  # positive means we are closer than opponent
            val = (adv, -us, -((rx + ry) % 3), -((rx * 7 + ry * 11) % 13))
            if local_best is None or val > local_best:
                local_best = val

        adv, neg_us, _, _ = local_best
        # Prefer grabbing sooner if tied in advantage
        us0 = min(dist(sx + dx, sy + dy, rx, ry) for rx, ry in resources)
        score = (adv, -us0)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]