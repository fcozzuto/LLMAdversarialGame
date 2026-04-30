def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick a target where I have a distance advantage (or smallest lead loss).
    best_t = resources[0]
    best_gap = None
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        gap = opd - myd  # higher is better for me
        if best_gap is None or gap > best_gap or (gap == best_gap and (myd < cheb(sx, sy, best_t[0], best_t[1]))):
            best_gap = gap
            best_t = (tx, ty)
    tx, ty = best_t

    # Score each move: maximize my closeness and minimize opponent closeness to the target.
    # Also lightly avoid stepping next to obstacles to reduce chance of being trapped.
    def adj_obstacle(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obstacles:
                    return 1
        return 0

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        myd1 = cheb(nx, ny, tx, ty)
        opd1 = cheb(ox, oy, tx, ty)  # opponent position unchanged this turn
        # My progress first, then deny opponent by choosing locally better target-following.
        # Incorporate whether I am becoming competitive against the current gap.
        val = (best_gap * 2) - myd1 * 5 + (-opd1) * 0.5 - adj_obstacle(nx, ny) * 0.3
        if val > best_val or (val == best_val and (dx, dy) == (0, 0)):
            best_val = val
            best_move = (dx, dy)

    # If all moves illegal (shouldn't happen), stay.
    if not legal(sx + best_move[0], sy + best_move[1]):
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]