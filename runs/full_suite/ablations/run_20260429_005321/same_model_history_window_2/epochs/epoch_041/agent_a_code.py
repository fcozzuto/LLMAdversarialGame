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

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Target: maximize advantage (opponent farther than us), otherwise minimize our distance.
    tx, ty = sx, sy
    if resources:
        best = None
        best_sc = -10**18
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Advantage-weighted: strongly prefer resources we can reach sooner and safely.
            sc = (do - ds) * 10 - ds
            # If tied, prefer farther from opponent to reduce contention.
            if do == ds:
                sc += (do - 1)
            if sc > best_sc:
                best_sc = sc
                best = (rx, ry)
        tx, ty = best
    else:
        # If no visible resources, drift to center while keeping distance from opponent.
        tx, ty = w // 2, h // 2

    # Choose move: approach target, avoid obstacles, and keep distance from opponent.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_from_o = cheb(nx, ny, ox, oy)
        # If the opponent is close, prioritize separation; otherwise prioritize approach.
        sc = -d_to_t * (2 if d_from_o > 2 else 1) + d_from_o * 0.7
        # Mild tie-break toward staying closer to board center for robustness.
        cx, cy = w // 2, h // 2
        sc -= 0.05 * cheb(nx, ny, cx, cy)
        if sc > best_score:
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]