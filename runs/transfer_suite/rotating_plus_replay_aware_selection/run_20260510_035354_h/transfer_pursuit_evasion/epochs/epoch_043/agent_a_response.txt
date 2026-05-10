def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles)

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_evader = ("evad" in self_role)
    opp_evader = ("evad" in opp_role) if opp_role else (not self_evader)

    moves = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1),
             (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    def neighbors(x, y):
        res = []
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) not in obs:
                res.append((nx, ny))
        return res

    options = neighbors(sx, sy)
    if not options:
        return [0, 0]

    # If we are pursuer: minimize distance to opponent; if we are evader: maximize.
    # Add a deterministic corner/edge bias to reduce zigzagging in open space.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best = None
    best_score = None

    # For evasion, bias toward the farthest corner from opponent; for pursuit, toward the nearest.
    target_corner = max(corners, key=lambda c: d2(c[0], c[1], ox, oy))
    # For pursuer bias, use the corner closest to opponent (more consistent pathing).
    pursuit_corner = min(corners, key=lambda c: d2(c[0], c[1], ox, oy))

    chasing = not self_evader  # pursuer
    for nx, ny in options:
        dist_to_opp = d2(nx, ny, ox, oy)
        if chasing:
            # minimize dist to opponent; also slightly align toward pursuit_corner
            corner_term = d2(nx, ny, pursuit_corner[0], pursuit_corner[1])
            score = -dist_to_opp * 1000 - corner_term
        else:
            # maximize dist to opponent; also slightly align toward target_corner
            corner_term = d2(nx, ny, target_corner[0], target_corner[1])
            score = dist_to_opp * 1000 + corner_term

        # tie-break deterministically: prefer moves with larger dx then dy then (x+y)
        if best is None:
            best = (nx, ny)
            best_score = score
        else:
            if score > best_score:
                best = (nx, ny)
                best_score = score
            elif score == best_score:
                bdx = best[0] - sx
                bdy = best[1] - sy
                ndx = nx - sx
                ndy = ny - sy
                if (ndx, ndy, nx + ny) > (bdx, bdy, best[0] + best[1]):
                    best = (nx, ny)

    dx = best[0] - sx
    dy = best[1] - sy
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]