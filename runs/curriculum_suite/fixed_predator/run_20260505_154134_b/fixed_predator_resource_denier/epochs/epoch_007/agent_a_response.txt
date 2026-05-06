def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        ax -= bx
        ay -= by
        return ax if ax >= 0 and ay >= 0 else (ay if ay >= 0 else -ax)

    def d(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    # Integer-safe chebyshev distance
    def cd(a, b):
        return d(a, b)

    def best_for_pos(px, py):
        if resources:
            best = None
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                ds = cd((px, py), (rx, ry))
                do = cd((ox, oy), (rx, ry))
                # Favor resources we can reach first; if opponent is closer, still try to race (deny).
                score = (do - ds) * 10 - ds + do
                # Small tiebreakers for stability
                t = rx * 0.01 + ry * 0.001
                val = score + t
                if best is None or val > best:
                    best = val
            if best is not None:
                return best
        # No usable resources: move to deny by reducing distance to opponent
        return -cd((px, py), (ox, oy))

    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        v = best_for_pos(nx, ny)
        if best_val is None or v > best_val:
            best_val = v
            best_move = [dx, dy]

    # If all moves land on obstacles/out of bounds, stay
    return best_move if best_val is not None else [0, 0]