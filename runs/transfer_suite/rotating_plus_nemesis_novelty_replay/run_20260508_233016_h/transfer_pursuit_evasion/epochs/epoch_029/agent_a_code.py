def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, dict):
            x = r.get("x", r.get("pos_x", r.get("px", None)))
            y = r.get("y", r.get("pos_y", r.get("py", None)))
            if x is not None and y is not None:
                resources.append((int(x), int(y)))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def best_target():
        if resources:
            best = None
            for (rx, ry) in resources:
                if not inb(rx, ry):
                    continue
                d = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
                if best is None or d < best[0]:
                    best = (d, rx, ry)
            if best:
                return best[1], best[2]
        corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
        tx, ty = max(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))
        return tx, ty

    tx, ty = best_target()

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist_to_t = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        dist_to_o = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        score = dist_to_o - dist_to_t
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]