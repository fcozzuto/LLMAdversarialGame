def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    grid_w = observation.get("grid_width", 8) or 8
    grid_h = observation.get("grid_height", 8) or 8

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_key = None
    for p in resources:
        if not (isinstance(p, (list, tuple)) and len(p) >= 2):
            continue
        rx, ry = p[0], p[1]
        if (rx, ry) in obs:
            continue
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        if ds == 0:
            return [0, 0]
        # Prefer resources we can arrive earlier; else still go for closest feasible.
        key = (-(do - ds), ds, do, -(rx + ry))
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        return [0, 0]

    tx, ty = best
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < grid_w and 0 <= ny < grid_h):
                continue
            if (nx, ny) in obs:
                continue
            # small obstacle field penalty
            penalty = 0
            for ax, ay in obstacles:
                if isinstance(ax, (list, tuple)) and len(ax) >= 2:
                    continue
            for ex, ey in obs:
                if abs(ex - nx) <= 0 and abs(ey - ny) <= 0:
                    penalty += 10
                elif abs(ex - nx) <= 1 and abs(ey - ny) <= 1:
                    penalty += 1
            d = md(nx, ny, tx, ty)
            # prioritize reducing distance; prefer moves that keep option to out-time opponent
            advantage = (md(ox, oy, tx, ty) - md(nx, ny, tx, ty))
            moves.append((d, -advantage, penalty, dx, dy))
    if not moves:
        return [0, 0]
    moves.sort()
    return [int(moves[0][3]), int(moves[0][4])]