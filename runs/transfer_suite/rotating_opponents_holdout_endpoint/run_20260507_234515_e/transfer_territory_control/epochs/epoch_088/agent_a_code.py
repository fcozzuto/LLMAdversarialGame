def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    resources = []
    for p in observation.get("resources") or []:
        try:
            resources.append((int(p[0]), int(p[1])))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18
    cx, cy = w // 2, h // 2

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_opp = abs(nx - ox) + abs(ny - oy)

        if resources:
            d_res = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
            nearest_bonus = 0
            for rx, ry in resources:
                if abs(nx - rx) <= 1 and abs(ny - ry) <= 1:
                    nearest_bonus = 5
                    break
        else:
            d_res = abs(nx - cx) + abs(ny - cy)
            nearest_bonus = 0

        score = -3 * d_res + d_opp + nearest_bonus
        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]