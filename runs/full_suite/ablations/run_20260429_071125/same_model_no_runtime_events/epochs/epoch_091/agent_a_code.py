def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if legal(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not legal(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    if resources:
        best_val = -10**18
        best_move = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # Choose a resource where we can beat the opponent (maximize margin), then minimize our distance
            val = -10**18
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Higher when we are closer than opponent; also slightly prefer nearer resources
                score = (do - ds) * 1000 - ds
                if score > val:
                    val = score
            # Tie-breaker: prefer moving toward the overall "resource gravity"
            gx = sum(r[0] for r in resources) / len(resources)
            gy = sum(r[1] for r in resources) / len(resources)
            val2 = val - 2 * cheb(nx, ny, int(gx + 0.5), int(gy + 0.5))
            if val2 > best_val:
                best_val = val2
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No visible resources: head toward the center to regain options
    cx, cy = w // 2, h // 2
    best_d = 10**9
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = cheb(nx, ny, cx, cy)
        if d < best_d:
            best_d = d
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]