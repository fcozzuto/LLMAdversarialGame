def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    res_set = set((p[0], p[1]) for p in resources)

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Immediate pickup if possible
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) in res_set and (nx, ny) not in obstacles:
            return [dx, dy]

    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_key = (-10**18, 10**9, -10**18)  # (margin, selfd, -oppd)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Pick resource that maximizes "win likelihood" from this next position
        local_best = None
        for rx, ry in resources:
            selfd = dist8(nx, ny, rx, ry)
            oppd = dist8(ox, oy, rx, ry)
            margin = oppd - selfd
            key = (margin, -selfd, -oppd, rx, ry)
            if local_best is None or key > local_best:
                local_best = key

        margin, neg_selfd, neg_oppd, rx, ry = local_best
        selfd = -neg_selfd
        oppd = -neg_oppd
        key = (margin, selfd, -oppd)
        if key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]