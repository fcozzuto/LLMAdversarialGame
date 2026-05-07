def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Adaptation for sweep_rows-like opponent: bias toward resources "in our side" along x,
    # so we contest earlier lanes rather than chase global nearest.
    prefer_right = sx > ox  # if we're to the right, prioritize larger x; else smaller x
    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        lane = rx if prefer_right else -rx
        # Prefer cells we can reach no worse; if tie, prioritize lane contest, then closer.
        key = (1 if sd > od else 0, sd - od, -lane, sd, rx + 31 * ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    nx, ny = sx + dx, sy + dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if valid(nx, ny):
        return [dx, dy]

    # Detour: choose among legal moves (including stay) minimizing distance to target.
    best_move = [0, 0]
    best_dist = cheb(sx, sy, tx, ty)
    for mdx in (-1, 0, 1):
        for mdy in (-1, 0, 1):
            x, y = sx + mdx, sy + mdy
            if not valid(x, y):
                continue
            d = cheb(x, y, tx, ty)
            # Deterministic tie-break by move order
            if d < best_dist or (d == best_dist and (mdx, mdy) < (best_move[0], best_move[1])):
                best_dist = d
                best_move = [mdx, mdy]
    return [int(best_move[0]), int(best_move[1])]