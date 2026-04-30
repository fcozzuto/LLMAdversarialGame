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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_obst(x, y):
        # Penalize moving near obstacles as a crude collision-avoidance heuristic.
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    return 1
        return 0

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    turn = int(observation.get("turn_index", 0) or 0)
    edge_bias = 0.15 if turn < 24 else 0.0  # earlier: avoid wasting time chasing middle too late

    best_move = (0, 0)
    best_val = None

    # Evaluate each move by racing for the best resource from the prospective position,
    # but also slightly favor staying away from obstacles and away from opponent when necessary.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            # Engine will keep us in place for invalid moves; treat it as staying.
            nx, ny = sx, sy
            dx, dy = 0, 0

        my_opp_dist = cheb(nx, ny, ox, oy)
        obst_pen = adj_obst(nx, ny)

        # Choose the target that best improves my lead (my distance advantage).
        # Objective: minimize (my_dist - 0.9*opp_dist) with additional small tie-breakers.
        best_t_val = None
        for tx, ty in resources:
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            # Negative is good (I am closer than opponent).
            v = myd - 0.9 * opd
            # Slight preference for resources that reduce risk of being cornered later
            # (pull away from map edges a bit after midgame).
            if edge_bias != 0.0:
                v += edge_bias * (min(tx, w - 1 - tx) + min(ty, h