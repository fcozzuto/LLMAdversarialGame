def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_resource_for(x, y):
        if not resources:
            return None, 0
        # Score favors closer to self and farther from opponent.
        best_t = None
        best_s = -10**18
        for rx, ry in resources:
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Deterministic tie-break on position.
            score = (-ds * 10) + (do * 3) - (rx * 0.01) - (ry * 0.001)
            if score > best_s:
                best_s = score
                best_t = (rx, ry)
        return best_t, best_s

    if resources:
        tx, ty = best_resource_for(sx, sy)[0]
        # If somehow none, fallback below.
        if tx is None:
            tx, ty = (w - 1, h - 1) if (ox + oy) < (sx + sy) else (0, 0)
    else:
        tx, ty = (w - 1, h - 1) if (ox + oy) < (sx + sy) else (0, 0)

    # Choose move that improves progress to chosen target, but also considers contesting the next best resource.
    next_best, _ = best_resource_for(sx, sy)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dcur = cheb(nx, ny, tx, ty)
        # Encourage moving toward any promising resource if current target is contested.
        t2, _ = best_resource_for(nx, ny)
        extra = 0
        if t2 is not None:
            extra = -cheb(nx, ny, t2[0], t2[1])
        # Also avoid letting opponent immediately get much closer to the target.
        dop = cheb(ox, oy, tx, ty)
        dop_next = cheb(nx, ny, tx, ty)  # proxy; deterministic shaping
        val = (-dcur * 20) + (extra * 5) + ((dop_next - dop) * 2)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]