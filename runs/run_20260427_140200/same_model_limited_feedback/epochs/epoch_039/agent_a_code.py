def choose_move(observation):
    W = observation.get("grid_width", 8)
    H = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set(tuple(p) for p in obstacles)
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def in_bounds(x, y):
        return 0 <= x < W and 0 <= y < H

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev distance

    best_move = (0, 0)
    best_score = None

    cx, cy = (W - 1) // 2, (H - 1) // 2

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        if resources:
            local_best = None
            for r in resources:
                rx, ry = r
                ds = dist((nx, ny), (rx, ry))
                do = dist((ox, oy), (rx, ry))
                if ds <= do:
                    score = (0, ds - do, ds, rx, ry)
                else:
                    score = (1, ds - do, ds, rx, ry)
                if local_best is None or score < local_best:
                    local_best = score
            score = local_best
        else:
            score = (0, dist((nx, ny), (cx, cy)), nx, ny)

        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]