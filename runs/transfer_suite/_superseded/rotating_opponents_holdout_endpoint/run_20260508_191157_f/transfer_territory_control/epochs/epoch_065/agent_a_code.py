def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if unclaimed:
        best_t = min(unclaimed, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
        tx, ty = best_t
        scored = []
        for dx, dy, nx, ny in legal:
            d = abs(nx - tx) + abs(ny - ty)
            scored.append((d, abs(nx - ox) + abs(ny - oy), dx, dy, nx, ny))
        _, _, dx, dy, _, _ = min(scored, key=lambda x: (x[0], -x[1], x[2], x[3]))
        return [dx, dy]
    else:
        scored = []
        for dx, dy, nx, ny in legal:
            d = abs(nx - ox) + abs(ny - oy)
            scored.append((-d, dx, dy))
        _, dx, dy = min(scored, key=lambda x: (x[0], x[1], x[2]))
        return [dx, dy]