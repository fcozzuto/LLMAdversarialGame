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

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_move = [0, 0]
    best_val = None

    moves = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not in_bounds(nx, ny):
            nx, ny = sx, sy
            dxm, dym = 0, 0
        val = None

        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources where we are at least as fast; maximize advantage.
            # Secondary: prefer smaller my distance; tertiary: prefer higher corner-sum (deterministic).
            advantage = opd - myd
            fast = 1 if myd <= opd else 0
            score = (fast * 1000) + (advantage * 50) - myd + ((rx + ry) * 0.001)
            if val is None or score > val:
                val = score

        # Deterministic tie-break: fixed move order via val comparison then lexicographic on move delta
        if best_val is None or val > best_val or (val == best_val and (dxm, dym) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dxm, dym]

    return best_move