def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs_set:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        best = (0, 0)
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            v = cheb(nx, ny, ox, oy)
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_val = None

    for rx, ry in resources:
        if (rx, ry) in obs_set:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        if sd == 0:
            return [0, 0]
        # We prefer arriving earlier; if we're behind, still consider the "least lost" one.
        target_score = (od - sd, -sd)

        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if (nx, ny) in obs_set:
                continue
            nsd = cheb(nx, ny, rx, ry)
            nod = cheb(ox, oy, rx, ry)
            val = (nod - nsd, -nsd, -cheb(nx, ny, ox, oy), target_score)
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]