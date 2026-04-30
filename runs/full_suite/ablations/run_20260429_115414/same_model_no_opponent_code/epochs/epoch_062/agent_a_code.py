def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def king(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose target with deterministic "win potential"
    best_t = None
    best_val = None
    for rx, ry in sorted(resources):
        myd = king((sx, sy), (rx, ry))
        opd = king((ox, oy), (rx, ry))
        # Favor resources where we are closer or opponent is far; prefer lower myd as tiebreaker.
        val = (opd - myd, -myd)
        if best_val is None or val > best_val:
            best_val = val
            best_t = (rx, ry)
    tx, ty = best_t

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort()  # deterministic tie-breaking order
    best_m = None
    best_m_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        myd2 = king((nx, ny), (tx, ty))
        # also account for blocking/contesting: if opponent can immediately steal, reduce value
        opd2 = king((ox, oy), (tx, ty))
        # Encourage staying aggressive: reduce our distance, increase opponent distance, avoid "zugzwang" where opponent gets closer by more than us.
        val = (-myd2, opd2 - myd2, -king((nx, ny), (ox, oy)))
        if best_m_val is None or val > best_m_val:
            best_m_val = val
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]