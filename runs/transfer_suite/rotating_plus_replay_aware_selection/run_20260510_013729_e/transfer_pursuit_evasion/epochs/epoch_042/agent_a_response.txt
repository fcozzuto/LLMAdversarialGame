def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role) or ("chase" in role) or ("hunter" in role)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def obstacle_penalty(x, y):
        if (x, y) in obs:
            return 10**7
        if not obs:
            return 0
        dmin = 10**9
        for bx, by in obs:
            d = abs(x - bx) + abs(y - by)
            if d < dmin:
                dmin = d
        return 50 / (1 + dmin)

    best_move = (0, 0)
    best_val = -10**18 if is_pursuer else 10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs:
            val = 10**10 if is_pursuer else -10**10
        else:
            d_op = man(nx, ny, ox, oy)
            corner = min(corners, key=lambda c: man(nx, ny, c[0], c[1]))
            # pursuer: minimize distance; evader: maximize distance; both: avoid obstacles/walls
            wall_pen = (0 if 0 < nx < w - 1 else 6) + (0 if 0 < ny < h - 1 else 6)
            obs_pen = obstacle_penalty(nx, ny)
            # tie-breaker: drift toward/away from opponent using distance to nearest corner opposite
            if is_pursuer:
                val = d_op + obs_pen + wall_pen - 0.02 * corner[1]  # tiny deterministic bias
                better = val < best_val
            else:
                val = d_op - obs_pen - wall_pen + 0.02 * (w - 1 - corner[0])
                better = val > best_val
        if is_pursuer:
            if better:
                best_val = val
                best_move = (dx, dy)
        else:
            if better:
                best_val = val
                best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]