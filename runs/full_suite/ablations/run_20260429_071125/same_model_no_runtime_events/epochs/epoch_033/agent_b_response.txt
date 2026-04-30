def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def king(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_move(nx, ny):
        # If no resources: go toward center while not walking into opponent.
        if not resources:
            cx, cy = w // 2, h // 2
            dcent = king(nx, ny, cx, cy)
            dopp = king(nx, ny, ox, oy)
            return -dcent + 0.1 * dopp

        # Evaluate contested resources: prefer those we are closer to than opponent.
        best = -10**18
        for rx, ry in resources:
            d_me = king(nx, ny, rx, ry)
            d_op = king(ox, oy, rx, ry)
            # Bias toward resources that are closer to us, but still keep overall progress.
            # Also add slight preference for nearer contested targets.
            contested = d_op - d_me  # positive if we are closer
            val = 8.0 * contested - 1.0 * d_me
            if (rx == ox and ry == oy):  # harmless special case
                val -= 5.0
            if val > best:
                best = val

        # Secondary term: avoid helping opponent by reducing our distance to what they can reach sooner.
        d_to_opp = king(nx, ny, ox, oy)
        best += 0.05 * d_to_opp
        return best

    # Deterministic tie-breaking: fixed order of dirs.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v = score_move(nx, ny)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]