def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = [tuple(p) for p in (observation.get("resources") or []) if p and (p[0], p[1]) not in obstacles]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        best_move = (0, 0)
        best_score = -10**18

        # Choose a "target" resource that's promising for us and less immediate for opponent
        target = resources[0]
        best_t = 10**18
        for rx, ry in resources:
            ts = cheb(sx, sy, rx, ry)
            to = cheb(ox, oy, rx, ry)
            # prioritize closer for self; penalize when opponent is also close
            val = ts * 10 - to
            if val < best_t:
                best_t = val
                target = (rx, ry)

        rx, ry = target
        for dx, dy, nx, ny in legal:
            on_res = 1 if (nx, ny) == (rx, ry) else 0
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer immediate capture; otherwise, reduce our distance and (slightly) avoid situations
            # where opponent is also very close to the same target.
            score = on_res * 10000 - ds * 20 - do * 2 + cheb(nx, ny, ox, oy) * 0.1
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # If no resources are visible, drift to center while avoiding obstacles and staying safe from opponent
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy, nx, ny in legal:
        score = -cheb(nx, ny, cx, cy) + cheb(nx, ny, ox, oy) * 0.05
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]