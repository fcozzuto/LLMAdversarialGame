def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    resources = sorted(resources)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_move = (0, 0)
    best_score = -10**18

    # Score each possible move by best achievable "distance advantage" over opponent to any resource.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        move_best = -10**18
        for tx, ty in resources:
            d_me = cheb(nx, ny, tx, ty)
            d_op = cheb(ox, oy, tx, ty)
            # Primary: increase margin (opponent farther). Secondary: reduce our distance.
            s = (d_op - d_me) * 100 - d_me
            # Tiny deterministic tie-break to prefer central-ish targets.
            s -= abs(tx - (w - 1) / 2) + abs(ty - (h - 1) / 2)
            if s > move_best:
                move_best = s

        if move_best > best_score:
            best_score = move_best
            best_move = (dx, dy)

    # If no valid moves were found (should be rare), stay.
    dx, dy = best_move
    if not (dx in (-1, 0, 1) and dy in (-1, 0, 1)):
        return [0, 0]
    return [dx, dy]