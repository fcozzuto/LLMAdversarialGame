def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) == 2:
            obstacles.add((p[0], p[1]))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def mhd(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def resource_order_key(r):
        x, y = r
        return (x, y)

    obstacles_dir_pen = {( -1, -1):0, (-1,0):0, (-1,1):0, (0,-1):0, (0,0):0, (0,1):0, (1,-1):0, (1,0):0, (1,1):0}
    # Small deterministic penalty if moving adjacent to an obstacle (to avoid getting stuck)
    for dx, dy in deltas:
        obstacles_dir_pen[(dx, dy)] = 0.0

    if not resources:
        best = (-10**18, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny): 
                continue
            score = -cheb(nx, ny, ox, oy) - 0.01 * (nx == 0 or ny == 0 or nx == w-1 or ny == h-1)
            if score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    resources_sorted = sorted([(r[0], r[1]) for r in resources], key=resource_order_key)

    best = (-10**18, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Prefer moves that make us relatively closer to resources vs opponent.
        best_r = None
        best_r_score = -10**18
        for rx, ry in resources_sorted:
            ds = mhd(nx, ny, rx, ry)
            do = mhd(ox, oy, rx, ry)
            # If we are closer than opponent, that's strongly good; otherwise discourage.
            lead = do - ds
            # Also discourage moving far from any resource.
            near = -ds
            score = 6.0 * (lead >= 0) + 0.8 * lead + 0.2 * near
            # Deterministic tiebreaker by resource coordinate
            score += -0.0001 * (rx * 8 + ry)
            if score > best_r_score:
                best_r_score = score
                best_r = (rx, ry)

        # Mildly avoid cornering against obstacles/edges; also prevent oscillation by preferring smallest delta id
        edge_pen = 0.01 * (nx == 0 or ny == 0 or nx == w-1 or ny == h-1)
        # Prefer reducing distance to opponent if we're not leading any resource
        opp_pen = 0.03 * (cheb(nx, ny, ox, oy))
        score_move = best_r_score - edge_pen - opp_pen

        if score_move > best[0]:
            best = (score_move, dx, dy)
    return [best[1], best[2]]