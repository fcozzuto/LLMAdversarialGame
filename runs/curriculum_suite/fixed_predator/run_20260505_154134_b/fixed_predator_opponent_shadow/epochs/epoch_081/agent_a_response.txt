def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
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
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def cell_blocked(x, y):
        return (x, y) in obs or not inb(x, y)

    if not resources:
        return [0, 0]

    # If we're on a resource, stay if it keeps us away from the opponent; otherwise step to the best nearby
    def best_for(x, y):
        best_key = None
        best_score = None
        for cx, cy in resources:
            if (cx, cy) in obs:
                continue
            self_d = cheb(x, y, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            # Key: maximize opp advantage we can steal, then prioritize closeness
            key = (opp_d - self_d, -self_d, -cx, -cy)
            if best_key is None or key > best_key:
                best_key = key
                best_score = (cx, cy)
        return best_score

    tx, ty = best_for(sx, sy)
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if cell_blocked(nx, ny):
                continue
            moves.append((dx, dy, nx, ny))

    # Local evaluation: head toward a target we can reach first, but avoid getting closer to opponent
    best = None
    best_val = None
    for dx, dy, nx, ny in moves:
        # Avoid opponent (shadow): penalize being closer after the move
        self_to_opp = cheb(nx, ny, ox, oy)
        # Resource pressure: choose best resource from the candidate cell
        t = best_for(nx, ny)
        if t is None:
            val = (-self_to_opp, 0)
        else:
            cx, cy = t
            self_d = cheb(nx, ny, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            # If we can arrive no later than opponent, strongly prefer
            steal = opp_d - self_d
            val = (steal, -self_d, -self_to_opp)
        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best