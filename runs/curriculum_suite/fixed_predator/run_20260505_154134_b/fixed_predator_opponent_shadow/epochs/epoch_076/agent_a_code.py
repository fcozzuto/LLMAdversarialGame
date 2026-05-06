def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best_move = [0, 0]
    best_val = None

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue

            # One-step lookahead: for this candidate position, evaluate best resource contest.
            best_for_move = None
            for cx, cy in resources:
                sd = cheb(nx, ny, cx, cy)
                od = cheb(ox, oy, cx, cy)
                # Prefer moves where we are closer than opponent; then prefer shorter self distance.
                val = (od - sd, -sd, -cx, -cy)
                if best_for_move is None or val > best_for_move:
                    best_for_move = val

            if best_for_move is None:
                continue

            if best_val is None or best_for_move > best_val:
                best_val = best_for_move
                best_move = [dx, dy]

    if best_val is None:
        return [0, 0]
    return best_move