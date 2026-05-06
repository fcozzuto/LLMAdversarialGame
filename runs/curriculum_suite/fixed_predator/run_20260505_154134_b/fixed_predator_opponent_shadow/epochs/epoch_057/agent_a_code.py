def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    def best_target(px, py):
        # New: secure-first policy. Prefer resources where we are clearly closer (opp_far - self_near).
        best = None
        best_key = None
        for cx, cy in resources:
            self_d = cheb(px, py, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            margin = opp_d - self_d
            # If we are not closer, still allow stealing but with less emphasis.
            closer_bonus = margin if margin > 0 else int(-2 * self_d)
            key = (closer_bonus, -cheb(px, py, cx, cy), -cx, -cy)
            if best_key is None or key > best_key:
                best_key = key
                best = (cx, cy)
        return best

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        tx, ty = best_target(nx, ny)
        self_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # New: maximize our advantage at the chosen target; tie-break deterministically.
        val = (opp_d - self_d, -self_d, -(tx + ty), -dx, -dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]