def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        move_best = None
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)

            # Resource is attractive if we can arrive earlier; otherwise it can help the denier.
            if sd < od:
                denial = 4.0 + (od - sd) * 0.6
            elif sd == od:
                denial = -0.4
            else:
                denial = -(2.0 + (sd - od) * 0.9)

            # Prefer fast collection and slightly prefer central-ish targets.
            urgency = 2.0 / (1 + sd)
            center = -0.01 * (abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2))

            val = denial + urgency + center + (od - sd) * 0.15
            if move_best is None or val > move_best:
                move_best = val

        # If multiple moves tie, prefer staying closer to keeping options (lower sd average to top few).
        if best is None or move_best > best:
            best = move_best
            best_move = [dx, dy]

    if best_move == [0, 0] and not inside(sx, sy):
        # In case our current position is somehow invalid, pick any valid move.
        for dx, dy in moves:
            if inside(sx + dx, sy + dy):
                return [dx, dy]

    return best_move