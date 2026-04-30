def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If no resources, head to the farthest corner from opponent to limit their progress.
    if not resources:
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        corners.sort(key=lambda c: (-cheb(c[0], c[1], ox, oy), c[0], c[1]))
        tx, ty = corners[0]
        best = (-10**18, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): continue
            score = -cheb(nx, ny, tx, ty)
            if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
                best = (score, dx, dy)
        return [best[1], best[2]]

    # Choose a target resource that we can reach earlier than the opponent (deterministically).
    targets = []
    for rx, ry in resources:
        dS = cheb(sx, sy, rx, ry)
        dO = cheb(ox, oy, rx, ry)
        # Prefer resources closer to us; penalize if opponent is much closer.
        lead = dO - dS
        # Tie-break deterministically by position.
        targets.append((lead, -dS, -dO, rx, ry))
    targets.sort(reverse=True)
    tx, ty = targets[0][3], targets[0][4]

    # One-step evaluation with opponent pressure.
    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny): continue
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        # Encourage reducing our distance while not letting opponent get relatively better.
        score = (-ds2) + 0.15 * (do2 - ds2)
        # Small secondary preference: move toward center to improve mobility if ds2 equal.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score += -0.01 * cheb(nx, ny, int(cx), int(cy))
        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    return [best[1], best[2]]