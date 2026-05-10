def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    best_move = [0, 0]
    best_rank = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy  # deterministic: avoid obstacles/out of bounds
        move_rank = None

        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            if nx == rx and ny == ry:
                rank = (0, 0, 0)
            else:
                reachable = 1 if myd <= opd else 0
                if reachable:
                    rank = (0, myd, -opd, rx + 7 * ry)
                else:
                    # Not reachable: try to increase (opd - myd) to deny/delay opponent effectively
                    diff = opd - myd
                    rank = (1, -diff, myd, rx + 7 * ry)

            if move_rank is None or rank < move_rank:
                move_rank = rank

        if best_rank is None or move_rank < best_rank:
            best_rank = move_rank
            best_move = [dx, dy]

    return best_move