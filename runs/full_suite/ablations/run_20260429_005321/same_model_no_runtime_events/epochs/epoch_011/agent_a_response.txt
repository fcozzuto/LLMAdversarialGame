def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            t = (p[0], p[1])
            if t not in obstacles:
                resources.append(t)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        best_move = (0, 0)
        for dx, dy, nx, ny in legal:
            k = (cheb(nx, ny, cx, cy), cheb(nx, ny, ox, oy), abs(dx) + abs(dy))
            if best is None or k < best:
                best, best_move = k, (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # Pick a target resource where the opponent is relatively farther than we are.
    # This is a deliberate shift: avoid tunneling the closest resource if the opponent can beat it.
    target = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        lead = opd - myd  # larger is better for us
        # prioritize: lead first, then be closer, then prefer remaining in our half (via center bias)
        k = (-lead, myd, cheb(rx, ry, (w - 1) // 2, (h - 1) // 2))
        if best_key is None or k < best_key:
            best_key, target = k, (rx, ry)

    rx, ry = target

    # Move: choose step that increases our lead to the target; tie-break by staying away from opponent
    # and reducing distance to the target.
    best = None
    best_move = (0, 0)
    for dx, dy, nx, ny in legal:
        myd2 = cheb(nx, ny, rx, ry)
        opd2 = cheb(ox, oy, rx, ry)  # opponent position unchanged this turn
        lead2 = opd2 - myd2
        # If lead is not improving, still move toward target, but avoid allowing opponent to immediately take closer resources.
        # Tie-break: farther from opponent and lower distance.
        k = (-lead2, myd2, cheb(nx, ny, ox, oy), abs(dx) + abs(dy))
        if best is None or k < best:
            best, best_move = k, (dx, dy)

    # Safety: if staying still is as good or better, prefer moving toward target anyway unless blocked by tie-breaks.
    return [int(best_move[0]), int(best_move[1])]