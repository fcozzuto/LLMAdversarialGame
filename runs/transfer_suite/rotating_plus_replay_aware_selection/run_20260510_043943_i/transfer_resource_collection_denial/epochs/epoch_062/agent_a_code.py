def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            nx, ny = sx, sy
        if nx == sx and ny == sy and (dx, dy) != (0, 0):
            continue

        # choose a single target resource after making the move
        best_target = None
        best_key = None
        for rx, ry in resources:
            if not cell_ok(rx, ry):
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # strong drive to be first/earlier, plus tie-break for resources farther from opponent
            # key: (smaller better)
            key = (sd, -(od - sd), -(rx + ry), (rx ^ ry) & 7)
            if best_key is None or key < best_key:
                best_key, best_target = key, (rx, ry)

        if best_target is None:
            continue

        rx, ry = best_target
        sd = man(nx, ny, rx, ry)
        od = man(ox, oy, rx, ry)
        # score the move itself: prefer immediate progress; penalize if opponent is clearly closer
        immediate = man(sx, sy, rx, ry) - sd  # positive if getting closer
        opp_pen = 0
        if od < sd:
            opp_pen = (sd - od + 1) * 50
        progress_bonus = immediate * 30
        # additional parity to reduce cycling deterministically
        parity = ((nx + ny + rx + ry) & 1) * 2
        val = progress_bonus + (od - sd) * 12 - sd - opp_pen + parity

        if best is None or val > best:
            best = val
            best_move = [nx - sx, ny - sy]

    return [int(best_move[0]), int(best_move[1])]