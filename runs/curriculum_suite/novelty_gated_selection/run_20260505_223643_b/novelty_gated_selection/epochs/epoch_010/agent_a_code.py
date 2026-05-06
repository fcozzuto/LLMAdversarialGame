def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_target = None
    best_val = None

    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Denier: prefer resources where we can arrive first; if not, pick one that forces the opponent to travel far.
        val = (do - ds) * 10.0
        val += (do - ds >= 0) * 6.0  # strong preference when we are not slower
        val += 0.05 * (cheb(sx, sy, rx, ry) - cheb(ox, oy, rx, ry))
        val += 0.001 * ((rx + 2 * ry) % 7)  # deterministic tie-break
        if best_val is None or val > best_val:
            best_val = val
            best_target = (rx, ry)

    rx, ry = best_target
    # Greedy step toward target, but avoid obstacles; deterministic tie-break by move order.
    best_step = None
    best_dist = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, rx, ry)
        # If we can't match distance, still prefer moves that keep us competitive vs opponent for the same target.
        competitiveness = cheb(ox, oy, rx, ry) - d
        key = (-(competitiveness), d)
        if best_step is None or key < best_dist:
            best_step = (dx, dy)
            best_dist = key

    return [best_step[0], best_step[1]] if best_step else [0, 0]