def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles)

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

    role = (observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    sgn = lambda v: 0 if v == 0 else (1 if v > 0 else -1)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    nearest_corner = min(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))
    ddx = sgn(nearest_corner[0] - ox)
    ddy = sgn(nearest_corner[1] - oy)
    trapx, trapy = ox + ddx, oy + ddy
    if not inb(trapx, trapy) or (trapx, trapy) in obs:
        trapx, trapy = nearest_corner

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy
            dx, dy = 0, 0

        if is_evader:
            dist = cheb(nx, ny, ox, oy)
            minobs = 0
            if obs:
                minobs = min(cheb(nx, ny, ex, ey) for ex, ey in obs)
            score = dist + 0.2 * minobs
            key = (-score, dx, dy)
        else:
            distO = cheb(nx, ny, ox, oy)
            distTrap = cheb(nx, ny, trapx, trapy)
            score = distO + 0.3 * distTrap
            key = (score, abs(dx) + abs(dy), dx, dy)

        if best is None or key < best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]