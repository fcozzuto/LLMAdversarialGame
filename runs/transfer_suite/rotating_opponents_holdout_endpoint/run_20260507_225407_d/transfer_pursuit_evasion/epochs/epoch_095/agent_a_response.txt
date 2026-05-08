def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role") or "").lower()
    opp_role = str(observation.get("opponent_role") or "").lower()
    we_evader = ("evader" in self_role) or ("evader" in opp_role and "pursuer" not in self_role)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    capture_radius = int(observation.get("capture_radius") or 0)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # If we are pursuer and can capture immediately, stay.
    if (not we_evader) and cheb(sx, sy, ox, oy) <= capture_radius:
        return [0, 0]

    # Prefer staying off obstacle-adjacent cells (robust vs forced traps).
    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def obstacle_risk(x, y):
        r = 0
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obstacles:
                r += 1
        return r

    # Deterministic tie-break: fixed ordering via score then lexical (dx,dy).
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        r = obstacle_risk(nx, ny)
        # Evader maximizes distance; pursuer minimizes distance.
        if we_evader:
            # Also bias toward the "farthest corner" from pursuer to break zigzags.
            corner_dist = max(cheb(nx, ny, 0, 0), cheb(nx, ny, w - 1, 0), cheb(nx, ny, 0, h - 1), cheb(nx, ny, w - 1, h - 1))
            score = (d * 10 + corner_dist) - (r * 3)
        else:
            score = (-d * 10) - (r * 3)
        if best is None or score > best_score:
            best_score = score
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]