def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def blocked(nx, ny):
        return not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles

    if not resources:
        return [0, 0]

    # Prefer resources we can reach no later than opponent; otherwise, pick the one
    # with best chance (opponent far, ours closer), then move one step toward it.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Key: prioritize ds<=do (win the race), then minimize ds, then maximize do.
        race = 0 if ds <= do else 1
        key = (race, ds, -do, (rx + ry), rx, ry)
        if best is None or key < best_key:
            best = (rx, ry)
            best_key = key

    tx, ty = best
    if sx == tx and sy == ty:
        return [0, 0]

    curd = cheb(sx, sy, tx, ty)
    best_move = (0, 0)
    best_new = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Greedy: strictly reduce distance; if tied, pick deterministic order by (dx,dy).
        if best_new is None or nd < best_new or (nd == best_new and (dx, dy) < best_move):
            if nd <= curd:
                best_new = nd
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]