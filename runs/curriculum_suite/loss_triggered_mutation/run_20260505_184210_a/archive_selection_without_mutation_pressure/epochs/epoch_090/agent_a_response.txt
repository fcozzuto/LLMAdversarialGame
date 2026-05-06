def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((r[0], r[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if inside(nx, ny) else [0, 0]

    opp_adv = 0
    best_action = None
    # Prefer resources where we are closer than opponent; tie-break by staying away from opponent.
    for dx, dy, nx, ny in legal:
        score = -md(nx, ny, ox, oy) * 0.15
        # Look at how "swingy" the best target is from next position.
        local_best = None
        for rx, ry in resources:
            myd = md(nx, ny, rx, ry)
            opd = md(ox, oy, rx, ry)
            # If we can reach sooner, this becomes strongly positive.
            gain = (opd - myd)
            # Mild preference for nearer resources overall.
            gain -= myd * 0.02
            if local_best is None or gain > local_best:
                local_best = gain
        if local_best is None:
            local_best = -md(nx, ny, ox, oy)
        score += local_best
        # Additional deterministic micro-heuristic: head generally toward the center of remaining resources.
        cx = 0
        cy = 0
        t = len(resources)
        for i, (rx, ry) in enumerate(resources):
            cx += rx if (i % 2 == 0) else rx
            cy += ry if (i % 2 == 0) else ry
        cx //= t
        cy //= t
        score -= md(nx, ny, cx, cy) * 0.005

        if best_action is None or score > best_action[0]:
            best_action = (score, dx, dy)

    return [best_action[1], best_action[2]]