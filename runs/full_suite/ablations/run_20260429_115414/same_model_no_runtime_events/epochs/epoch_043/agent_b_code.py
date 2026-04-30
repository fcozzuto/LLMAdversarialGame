def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        tx, ty = (ox, oy)
    else:
        best = None
        for rx, ry in resources:
            d = abs(rx - sx) + abs(ry - sy)
            if best is None or d < best[0] or (d == best[0] and (rx, ry) < best[1]):
                best = (d, (rx, ry))
        tx, ty = best[1]

    def score(nx, ny):
        if not valid(nx, ny):
            return 10**9
        d = abs(tx - nx) + abs(ty - ny)
        # Slight preference to avoid stepping adjacent to opponent
        adj = max(abs(ox - nx), abs(oy - ny))  # 0..inf
        return d * 10 + (0 if adj > 1 else 20 if adj == 1 else 80)

    best_move = (0, 0)
    best_val = 10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        val = score(nx, ny)
        if val < best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move