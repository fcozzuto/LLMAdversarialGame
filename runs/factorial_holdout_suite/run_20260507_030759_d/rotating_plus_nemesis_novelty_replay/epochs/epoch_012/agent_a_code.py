def choose_move(observation):
    def xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        return 0, 0

    def inb(x, y, w, h):
        return 0 <= x < w and 0 <= y < h

    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = xy(observation.get("self_position", [0, 0]))
    ox, oy = xy(observation.get("opponent_position", [7, 7]))
    resources = [xy(r) for r in (observation.get("resources", []) or [])]
    obstacles = set(xy(o) for o in (observation.get("obstacles", []) or []))

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    def cheb(a, b):
        return max(abs(b[0] - a[0]), abs(b[1] - a[1]))

    def cell_score(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        if resources:
            best = 10**9
            for rx, ry in resources:
                sd = cheb((nx, ny), (rx, ry))
                od = cheb((ox, oy), (rx, ry))
                # Prefer resources we reach no later than opponent, then closer to us.
                # Small bias for moving toward resources even if contested.
                val = (od - sd) * 10 - sd
                if sd == 0:
                    val += 200  # immediate collection
                if val < best:
                    best = val
            # Convert "lower is better" best into maximizing
            return -best
        # No visible resources: drift toward center while keeping distance from opponent
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        to_center = abs(nx - cx) + abs(ny - cy)
        to_opp = cheb((nx, ny), (ox, oy))
        return -to_center + to_opp * 0.05

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny, w, h):
            continue
        v = cell_score(nx, ny)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]