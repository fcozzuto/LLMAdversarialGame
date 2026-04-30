def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if p is not None and len(p) == 2:
            obstacles.add((p[0], p[1]))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        best = (-10**18, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            # Tie-break: prefer moving away from edges while approaching opponent (aggressive endgame)
            edge = (nx == 0) + (ny == 0) + (nx == w - 1) + (ny == h - 1)
            sc = -cheb(nx, ny, ox, oy) - 0.05 * edge
            if sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    best = (-10**18, 0, 0)
    # Look for a target where we are relatively closer than the opponent.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        best_rel = 10**18
        best_abs = 10**18
        # Also add mild repulsion from being dominated everywhere.
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            rel = ds - do  # smaller is better (we're closer than opponent)
            if rel < best_rel:
                best_rel = rel
            if ds < best_abs:
                best_abs = ds
        # Score: primary is relative advantage; secondary encourages approaching some resource.
        # Penalize dominated moves where best_rel is positive.
        dominated_pen = 0.0
        if best_rel > 0:
            dominated_pen = 2.0 * best_rel
        # Slightly prefer moves that reduce our absolute distance to the best resource.
        sc = -best_rel - dominated_pen - 0.15 * best_abs
        if sc > best[0]:
            best = (sc, dx, dy)
    return [best[1], best[2]]