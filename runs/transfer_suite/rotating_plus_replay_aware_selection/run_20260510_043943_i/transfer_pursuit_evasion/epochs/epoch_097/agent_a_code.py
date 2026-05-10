def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("fugitive" in role)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # If evader, go to farthest corner from pursuer; else go to nearest corner (less useful but deterministic)
    if is_evader:
        target_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    else:
        target_corner = min(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    moves = []
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny):
                moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    # Greedy 1-step with tie-breaks toward/away from opponent; evader also prefers target corner
    best = None
    for dx, dy, nx, ny in moves:
        d_opp = cheb(nx, ny, ox, oy)
        d_corner = cheb(nx, ny, target_corner[0], target_corner[1])
        # small deterministic tie-break: prefer diagonal movement when useful
        diag_bias = 0 if (dx == 0 or dy == 0) else 0.001
        # If evader, maximize distance and move toward chosen corner; if pursuer, minimize distance and move away from corner bias slightly
        if is_evader:
            score = (d_opp * 1000.0) + (-d_corner * 2.0) + diag_bias
            better = (best is None) or (score > best[0])
        else:
            score = (-d_opp * 1000.0) + (-d_corner * 0.2) + diag_bias
            better = (best is None) or (score > best[0])
        if better:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]