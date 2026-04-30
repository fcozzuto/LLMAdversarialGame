def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if not resources:
            # Fallback: head toward opponent's side while avoiding obstacles via simple gradient.
            tx, ty = (w - 1, h - 1) if (sx + sy) <= (ox + oy) else (0, 0)
            val = -d2(nx, ny, tx, ty) - 0.001 * d2(nx, ny, ox, oy)
        else:
            val = -d2(nx, ny, ox, oy) * 0.02  # slight pressure away from opponent
            # Choose move that improves our race to high-value resources.
            for rx, ry in resources:
                my = d2(nx, ny, rx, ry)
                opp = d2(ox, oy, rx, ry)
                # If we're closer, get a big bonus; otherwise smaller penalty.
                race = (opp - my)
                val += (race * 10.0) - (my * 0.15)
        # Deterministic tie-breaking by first best encountered (dirs order).
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]