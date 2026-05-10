def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unT = set()
    for p in observation.get("unclaimed_cells") or []:
        if len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unT.add((x, y))

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best = None
    best_score = -10**18
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def score_cell(x, y):
        s = 0
        if (x, y) == (ox, oy):
            s -= 1000000
        if (x, y) in unT:
            s += 2000
        s += -abs(x - cx) - abs(y - cy)
        s += abs(x - sx) * 0  # keep deterministic, no-op
        s += -2 * (abs(x - ox) + abs(y - oy))
        return s

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            sc = score_cell(nx, ny)
            if sc > best_score or (sc == best_score and (dx, dy) < best):
                best_score = sc
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]