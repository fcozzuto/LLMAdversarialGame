def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(map(tuple, observation.get("obstacles", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        # Chebyshev distance on grid with 8-neighborhood
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    def adj_obstacles(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    def legal_steps(x, y):
        out = []
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                out.append((dx, dy, nx, ny))
        if not out:
            return [(0, 0, x, y)]
        return out

    def pick_target(myx, myy, opx, opy):
        best = None
        for tx, ty in resources:
            if (tx, ty) in obstacles:
                continue
            myd = md(myx, myy, tx, ty)
            opd = md(opx, opy, tx, ty)
            contest = 1 if myd <= opd else 0
            center = - (abs(tx - (w - 1) / 2) + abs(ty - (h - 1) / 2))
            adj = -adj_obstacles(tx, ty)
            # Prefer: can contest -> want larger (opd-myd), then minimize myd, avoid adjacency
            key = (contest, opd - myd, -myd, adj, center, -tx, -ty)
            if best is None or key > best[0]:
                best = (key, tx, ty)
        if best is None:
            return resources[0]
        return (best[1], best[2])

    my_target = pick_target(sx, sy, ox, oy)
    tx, ty = my_target
    my_is_on = (sx, sy) == (tx, ty)

    # Estimate opponent greedy step toward its best current target
    op_target = pick_target(ox, oy, sx, sy)
    otx, oty = op_target
    op_best = None
    for dx, dy, nx, ny in legal_steps(ox, oy):
        dist = md(nx, ny, otx, oty)
        # deterministic tie-break
        key = (dist, dx, dy, nx, ny)
        if op_best is None or key < op_best[0]:
            op_best = (key, nx, ny)
    onx, ony = op_best[1], op_best[2]

    best_move = (0, 0)
    best_val = None
    for dx, dy,