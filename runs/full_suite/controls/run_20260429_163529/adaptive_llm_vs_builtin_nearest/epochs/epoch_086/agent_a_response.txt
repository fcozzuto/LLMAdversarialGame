def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Target: pick a resource where we are relatively closer than opponent; otherwise closest for us.
    best = None
    best_val = None
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        rel = d_me - d_op  # negative means we are winning that resource race
        val = rel * 1000 + d_me  # strong priority to race advantage, then finish time
        if best is None or val < best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Evaluate next move: move toward target; if tie, prefer increasing distance from opponent.
    best_move = (0, 0)
    best_cost = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_next = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # If opponent is very close, prioritize safety slightly.
        cost = d_next * 10 - d_opp
        if best_cost is None or cost < best_cost:
            best_cost = cost
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]