def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    opp_center_bias = md(ox, oy, cx, cy)  # deterministic float

    def cell_score(nx, ny):
        if resources:
            best = None
            for rx, ry in resources:
                ds = md(nx, ny, rx, ry)
                do = md(ox, oy, rx, ry)
                # Prefer targets where we are closer; also favor closer overall.
                # Include a small penalty if opponent is already much closer.
                delta = ds - do
                ahead_bonus = -50 if delta < 0 else 0
                contention_penalty = 5 * (delta if delta > 0 else 0)
                close_bonus = -ds
                center = md(nx, ny, cx, cy)
                s = ahead_bonus + close_bonus - contention_penalty + 0.05 * center + 0.01 * opp_center_bias
                if best is None or s < best:
                    best = s
            return best
        else:
            # No resources: go toward center, but slightly away from opponent.
            center = md(nx, ny, cx, cy)
            away = md(nx, ny, ox, oy)
            return center - 0.1 * away

    best = None
    best_move = (0, 0)
    for dx, dy, nx, ny in candidates:
        s = cell_score(nx, ny)
        key = (s, dx, dy)  # deterministic tie-break
        if best is None or key < best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]