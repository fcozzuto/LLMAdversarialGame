def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Pick target resource by "contest advantage": opponent distance - self distance (larger is better).
    best_key = None
    best_t = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        margin = od - sd
        key = (margin, -sd, -rx, -ry)  # deterministic tie-break
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)
    rx, ry = best_t

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_sd = cheb(sx, sy, rx, ry)

    # Local obstacle-aware move choice: maximize opponent-self distance advantage after move, then minimize self distance to target.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            nx, ny = sx, sy
        if (nx, ny) in obs:
            nx, ny = sx, sy

        sd = cheb(nx, ny, rx, ry)
        # Use opponent current position (opponent doesn't move this turn for our decision).
        od = cheb(ox, oy, rx, ry)
        margin = od - sd
        # Encourage progress; slightly discourage no-progress moves.
        progress = 1 if sd < cur_sd else 0
        key = (margin, progress, -sd, -dx, -dy)
        if best is None or key > best[0]:
            best = (key, [dx if inside(sx + dx, sy + dy) else 0, dy if inside(sx + dx, sy + dy) else 0])

    return best[1]