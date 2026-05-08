def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    sr = (observation.get("self_role", "") or "").lower()
    orr = (observation.get("opponent_role", "") or "").lower()
    flee = ("evader" in sr) or ("runner" in sr)

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)
        val = d if flee else -d
        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    return [best[0], best[1]]