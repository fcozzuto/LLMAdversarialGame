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
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Decide best move by maximizing "contest margin" after our move.
    best_move = [0, 0]
    best_val = None

    # Deterministic move ordering favors reducing cheb distance to a good contest target.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            moves.append((dx, dy))
    moves.sort(key=lambda m: (-(m[0] * (ox - sx) + m[1] * (oy - sy)), m[0], m[1]))
    moves = [(0, 0)] + moves

    # Precompute opp distances to each resource for speed and determinism.
    opp_ds = []
    for rx, ry in resources:
        opp_ds.append((int(rx), int(ry), cheb(ox, oy, int(rx), int(ry))))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # contest margin: for each resource, how much closer opponent is than us (bigger is better)
        # We take the best resource we can "claim" by being relatively faster than opponent.
        local_best = None
        nearest_self = None
        for rx, ry, od in opp_ds:
            sd = cheb(nx, ny, rx, ry)
            margin = od - sd  # positive means we are closer than opp
            # Prefer being able to get *some* resource; then keep us near that target.
            key = (margin, -sd, -rx, -ry)
            if local_best is None or key > local_best:
                local_best = key
                nearest_self = sd
        # Additional term: also reduce opponent closeness by not drifting toward where opp already is too favorable.
        # This helps change behavior when improvement stalls.
        opp_dir_bonus = -cheb(nx, ny, ox, oy)
        val = (local_best[0], local_best[1], opp_dir_bonus)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move