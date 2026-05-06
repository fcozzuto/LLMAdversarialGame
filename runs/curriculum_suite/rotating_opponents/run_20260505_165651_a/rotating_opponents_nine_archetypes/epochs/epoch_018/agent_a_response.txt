def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    best_move = (0, 0)
    best_val = None

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny):
            continue

        move_best = None
        for rx, ry in resources:
            ds = king_dist(nx, ny, rx, ry)
            do = king_dist(ox, oy, rx, ry)
            lead = do - ds
            center_pen = abs(rx - cx) + abs(ry - cy)
            # Prefer winning tempo; if not winning, minimize how badly we're behind.
            val = lead - 0.25 * ds - 0.01 * center_pen
            if move_best is None or val > move_best:
                move_best = val

        # If no resource reachable (unlikely), just keep safe.
        if move_best is None:
            move_best = -10**9

        # Extra tie-breakers: avoid running directly into opponent pressure.
        opp_step = king_dist(nx, ny, ox, oy)
        val2 = move_best - 0.02 * opp_step

        if best_val is None or val2 > best_val:
            best_val = val2
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]