def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x, y):
        return abs(x - ox) + abs(y - oy)

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        d = man(nx, ny)

        # Prefer moving toward opponent in both axes (cuts off more effectively)
        toward_x = 0 if ox == nx else (-1 if ox < nx else 1)
        toward_y = 0 if oy == ny else (-1 if oy < ny else 1)
        diag_bias = -1 if (toward_x != 0 and toward_y != 0 and abs(dx) == 1 and abs(dy) == 1) else 0

        # Mild penalty for staying (helps avoid local minima)
        stay_pen = 1 if (dx == 0 and dy == 0) else 0

        score = d + stay_pen + (0.1 if diag_bias else 0.0) + (0.01 * (abs(dx) + abs(dy)))

        if best_score is None or score < best_score:
            best_score = score
            best = [dx, dy]
        elif score == best_score and best is not None:
            # Deterministic tie-break
            if (dx, dy) < (best[0], best[1]):
                best = [dx, dy]

    if best is None:
        # If completely blocked, take the first valid in-bounds move (or stay)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    return best