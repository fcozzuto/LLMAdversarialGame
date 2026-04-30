def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in obstacles:
                return [int(dx), int(dy)]
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18
    best_sd = 10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        # Prefer a resource where we have a reach advantage over the opponent.
        local_best_gap = -10**18
        local_best_sd = 10**9
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            gap = od - sd  # positive means we can reach sooner (or already there)
            if gap > local_best_gap or (gap == local_best_gap and sd < local_best_sd):
                local_best_gap = gap
                local_best_sd = sd

        # Combine: maximize reach advantage, then closeness to that target.
        val = local_best_gap * 1000 - local_best_sd
        if val > best_val or (val == best_val and local_best_sd < best_sd):
            best_val = val
            best_sd = local_best_sd
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]