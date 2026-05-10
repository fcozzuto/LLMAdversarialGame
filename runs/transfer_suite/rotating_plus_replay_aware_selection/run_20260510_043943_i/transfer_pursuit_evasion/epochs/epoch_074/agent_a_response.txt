def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    is_pursuer = "pursuer" in self_role

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    obs_list = list(obstacles)

    def obs_pen(x, y):
        if not obs_list:
            return 0.0
        md = 10**9
        for bx, by in obs_list:
            d = abs(x - bx) + abs(y - by)
            if d < md: md = d
        if md <= 0: return 1e6
        return 1.0 / md

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    sx_f, sy_f = sx, sy

    best = [0, 0]
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        d_to_opp = cheb(nx, ny, ox, oy)
        p = obs_pen(nx, ny)

        if is_pursuer:
            # chase: primary minimize distance, secondary keep away from obstacles
            # tie-break deterministically: prefer diagonal when it reduces distance
            diag = 1 if dx != 0 and dy != 0 else 0
            val = (d_to_opp * 1000.0) - (diag * 5.0) + (p * 50.0)
            better = (best_val is None) or (val < best_val)
        else:
            # evade: primary maximize distance; secondary move toward farthest corner
            dc = cheb(nx, ny, far_corner[0], far_corner[1])
            # "wall runner" bias: favor corner-aligned moves by rewarding larger corner chebyshev
            val = (-d_to_opp * 1000.0) + (-dc * 10.0) + (p * 200.0)
            better = (best_val is None) or (val < best_val)  # we minimize val

        if better:
            best_val = val
            best = [dx, dy]

    # if all moves invalid (shouldn't happen), stay
    if best is None:
        return [0, 0]
    return best