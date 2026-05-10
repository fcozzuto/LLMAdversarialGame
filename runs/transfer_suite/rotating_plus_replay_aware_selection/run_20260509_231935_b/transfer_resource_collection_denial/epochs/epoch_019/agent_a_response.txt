def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))

    # If no resources visible, move toward center but away from opponent's approach direction
    if not resources:
        cx, cy = w // 2, h // 2
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            v = -dist8(nx, ny, cx, cy) + 0.6 * dist8(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose a target resource where we can arrive earlier than opponent (greedy contest)
    best_target = None
    best_score = -10**18
    for rx, ry in resources:
        od = dist8(ox, oy, rx, ry)
        sd = dist8(sx, sy, rx, ry)
        # Prefer immediate value, and advantage in arrival time; slight preference for closer overall
        score = 300 - 3 * sd + 6 * (od - sd) - 0.5 * (rx - sx) * 0 - 0.2 * (ry - sy) * 0
        if score > best_score:
            best_score = score
            best_target = (rx, ry)

    tx, ty = best_target

    # Pick next move among legal deltas that improves distance to target and reduces opponent distance
    best_move = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        sd = dist8(nx, ny, tx, ty)
        od = dist8(nx, ny, ox, oy)
        adv = dist8(nx, ny, tx, ty) - dist8(ox, oy, tx, ty)
        v = 30 - 4 * sd + 0.8 * (dist8(nx, ny, ox, oy) - dist8(sx, sy, ox, oy)) - 0.3 * od - 2.0 * adv
        if (dx, dy) == (0, 0):
            v -= 0.15  # encourage movement
        if v > bestv:
            bestv = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]