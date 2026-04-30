def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        dx = 0
        dy = 0
        return [dx, dy]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose a target resource we can plausibly reach before/with less race disadvantage.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer advantage; if close, prefer lower ds and closer to center to reduce edge trapping.
        center_pen = abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)
        adv = ds - do  # smaller is better
        if ds <= do + 1:
            key = (adv, ds, center_pen)
        else:
            key = (adv + 3, ds + 2, center_pen + 1)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Greedy one-step selection: move toward target while also discouraging getting cornered/being overtaken.
    best_step = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        ns = cheb(nx, ny, tx, ty)
        cs = cheb(ox, oy, tx, ty)
        # Score: primarily reduce distance to target; then reduce distance to opponent's target race; then increase separation.
        score = (ns, (ns - cs), -cheb(nx, ny, ox, oy), abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))
        if best_score is None or score < best_score:
            best_score = score
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]