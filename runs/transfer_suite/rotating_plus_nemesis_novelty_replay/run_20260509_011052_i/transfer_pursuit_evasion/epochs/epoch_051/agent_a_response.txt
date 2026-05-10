def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in self_role) and ("evader" not in self_role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def mobility(x, y):
        m = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                m += 1
        return m

    # Corner-biased target: pursuer tries to cut off; evader tries to run to a far corner.
    if corners:
        if pursuer:
            trap_corner = max(corners, key=lambda c: cheb(sx, sy, c[0], c[1]))
        else:
            trap_corner = min(corners, key=lambda c: cheb(sx, sy, c[0], c[1]))
    else:
        trap_corner = (w - 1, h - 1)

    # Intercept/cutoff point adjacent to opponent along direction to trap corner
    dxo = trap_corner[0] - ox
    dyo = trap_corner[1] - oy
    step_x = 0 if dxo == 0 else (1 if dxo > 0 else -1)
    step_y = 0 if dyo == 0 else (1 if dyo > 0 else -1)
    cut_x, cut_y = ox + step_x, oy + step_y
    if not valid(cut_x, cut_y):
        cut_x, cut_y = ox, oy

    # Simple evaluation
    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if pursuer:
            dist_to_opp = cheb(nx, ny, ox, oy)
            dist_to_cut = cheb(nx, ny, cut_x, cut_y)
            score = (-1000 * dist_to_opp) + (-50 * dist_to_cut) + (3 * mobility(nx, ny))
            # tie-break deterministically toward matching dx,dy order
        else:
            dist_to_opp = cheb(nx, ny, ox, oy)
            dist_to_corner = cheb(nx, ny, trap_corner[0], trap_corner[1])
            score = (1000 * dist_to_opp) + (20 * dist_to_corner) + (1 * mobility(nx, ny))
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]