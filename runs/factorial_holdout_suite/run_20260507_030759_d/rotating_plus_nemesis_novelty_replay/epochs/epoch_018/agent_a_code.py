def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    if not resources:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose a move that maximizes the best "win margin" resource we can aim for after the move.
    best_cell = (sx, sy)
    best_key = (-10**18, 10**18, 10**18, 10**18)  # (margin, self_dist, row_bonus, -x+y tie)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # For each reachable cell, consider aiming at the best resource from there.
        cell_best = (-10**18, 10**18, -10**18, 10**18)
        for rx, ry in resources:
            self_d = man((nx, ny), (rx, ry))
            opp_d = man((ox, oy), (rx, ry))
            margin = opp_d - self_d
            row_bonus = 1 if ry != oy else 0  # disrupt opponent sweep_rows tendency
            # If immediate collect, heavily prefer it.
            imm = 1 if self_d == 0 else 0
            # Deterministic tie: prefer larger margin, then immediate, then smaller self_d, then row_bonus, then x+y.
            key = (margin + imm * 1000, self_d, -row_bonus, rx + ry)
            if key > cell_best:
                cell_best = key
        if cell_best > best_key:
            best_key = cell_best
            best_cell = (nx, ny)

    bx, by = best_cell
    dx, dy = bx - sx, by - sy
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]