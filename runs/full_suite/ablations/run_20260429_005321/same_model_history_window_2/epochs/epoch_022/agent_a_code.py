def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    neigh8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def obst_adj_pen(x, y):
        pen = 0
        for dx, dy in neigh8:
            if (x + dx, y + dy) in obstacles:
                pen += 1
        return pen

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18
    rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))

    for dx, dy in moves:
        nx = sx + dx; ny = sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        my_pen = obst_adj_pen(nx, ny)
        # Evaluate best immediate target; reward denying opponent access.
        val = -0.25 * my_pen - 0.05 * cheb(nx, ny, ox, oy)
        if resources:
            best_t = -10**18
            for rx, ry in resources:
                d1 = cheb(nx, ny, rx, ry)
                d2 = cheb(ox, oy, rx, ry)
                # If opponent can reach no later, resource is contested: heavily discounted.
                contest = 1 if d2 <= d1 else 0
                score = (12 - d1) + 0.2 * rem
                score -= 8.0 * contest
                # Prefer moves that reduce distance faster than opponent.
                score += 0.5 * (d2 - d1)
                if score > best_t:
                    best_t = score
            val += best_t
        # Small deterministic tie-break: prefer increasing dx, then dy
        val += 1e-6 * (dx * 3 + dy)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]