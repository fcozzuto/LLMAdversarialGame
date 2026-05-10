def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Target selection: race the opponent; if no winning race, pick the best contest/deny target.
    best = resources[0]
    best_score = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        lead = opd - myd  # positive => we reach earlier
        d2 = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
        # Strongly prefer earlier-than-opponent, then closer, then far from opponent.
        score = lead * 100 - myd * 5 + (opd - myd) * 2 - d2 * 0.01
        if best_score is None or score > best_score:
            best_score = score
            best = (rx, ry)

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def cell_ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    # If we are on a target cell, stay (resource collection handled by engine).
    if (sx, sy) == (tx, ty):
        return [0, 0]

    # Move to reduce our chebyshev distance to target, with a small anti-opponent term.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Encourage keeping lead if already ahead; otherwise fastest approach.
        val = -myd * 10 + (opd - myd) * 2 - (abs(dx) + abs(dy)) * 0.01
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]