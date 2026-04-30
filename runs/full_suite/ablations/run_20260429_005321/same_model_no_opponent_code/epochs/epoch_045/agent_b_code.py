def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    tx, ty = (w // 2, h // 2)
    if resources:
        best = None
        for rx, ry in resources:
            d = (sx - rx) * (sx - rx) + (sy - ry) * (sy - ry)
            if best is None or d < best[0] or (d == best[0] and (rx < best[1][0] or (rx == best[1][0] and ry < best[1][1]))):
                best = (d, (rx, ry))
        tx, ty = best[1]

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        score = 0
        score -= (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        score += -((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)) // 10
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    if inb(sx, sy):
        return [best_move[0], best_move[1]]
    for dx, dy in dirs:
        if inb(sx + dx, sy + dy):
            return [dx, dy]
    return [0, 0]