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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        ax = ax - bx
        if ax < 0:
            ax = -ax
        ay = ay - by
        if ay < 0:
            ay = -ay
        return ax + ay

    if not resources:
        return [0, 0]

    best_move = [0, 0]
    best_ms = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            nx, ny = sx, sy
            if nx == sx and ny == sy and (dx, dy) != (0, 0):
                continue

        move_best = None
        for rx, ry in resources:
            if not cell_ok(rx, ry):
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd
            score = (-adv, sd, abs(rx - nx) + abs(ry - ny), rx, ry)
            if move_best is None or score < move_best:
                move_best = score

        if move_best is None:
            move_best = (0, 10**9, 10**9, -1, -1)

        if best_ms is None or move_best < best_ms or (move_best == best_ms and [dx, dy] < best_move):
            best_ms = move_best
            best_move = [dx, dy]

    return best_move