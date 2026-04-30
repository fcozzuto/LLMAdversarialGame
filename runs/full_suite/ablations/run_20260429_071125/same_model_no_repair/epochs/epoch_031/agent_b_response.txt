def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            nx, ny = sx, sy
            dx, dy = 0, 0

        if not resources:
            # Move toward center when no resources exist.
            val = cheb(nx, ny, cx, cy) + 0.15 * cheb(nx, ny, ox, oy)
            key = (val, dx, dy)
        else:
            # Pick move that gives best "race" advantage to some resource.
            best_r = None
            best_r_val = None
            for rx, ry in resources:
                my_d = cheb(nx, ny, rx, ry)
                opp_d = cheb(ox, oy, rx, ry)
                # If we step onto the resource cell, that's best.
                if my_d == 0:
                    r_val = -1000.0 + 0.01 * cheb(ox, oy, cx, cy)
                else:
                    r_val = my_d - 0.35 * opp_d + 0.02 * cheb(nx, ny, cx, cy)
                if best_r_val is None or r_val < best_r_val:
                    best_r_val = r_val
                    best_r = (rx, ry)
            # Secondary tie-break: avoid making opponent closer to our best target.
            bx, by = best_r
            opp_after = cheb(nx, ny, ox, oy)
            val = best_r_val + 0.02 * cheb(nx, ny, bx, by) + 0.01 * opp_after
            key = (val, dx, dy)

        if best_val is None or key < best_val:
            best_val = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]