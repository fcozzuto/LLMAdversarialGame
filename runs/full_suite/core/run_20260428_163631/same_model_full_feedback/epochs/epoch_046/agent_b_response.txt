def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = w // 2, h // 2
        best_move = (0, 0)
        best_d = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                d = cheb(nx, ny, tx, ty)
                if d < best_d:
                    best_d = d
                    best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    def resource_value(mx, my):
        # Prefer resources where we improve relative advantage vs opponent.
        best = -10**18
        for rx, ry in resources:
            md = cheb(mx, my, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Small tie-break: prefer being closer to the board center if equally good.
            center_bias = -0.01 * cheb(mx, my, w // 2, h // 2)
            val = (od - md) + center_bias
            # Strongly encourage direct pickup move if adjacent (or on it).
            if md == 0:
                val += 1000.0
            elif md == 1:
                val += 5.0
            if val > best:
                best = val
        return best

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # Also add a mild "escape from opponent proximity" term to avoid being pinned near their target.
        opp_prox = cheb(nx, ny, ox, oy)
        score = resource_value(nx, ny) + 0.02 * opp_prox
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]