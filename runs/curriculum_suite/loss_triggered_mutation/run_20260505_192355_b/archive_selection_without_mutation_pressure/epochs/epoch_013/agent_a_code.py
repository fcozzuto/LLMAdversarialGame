def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def edge_bonus(x, y):
        d = min(x, w - 1 - x, y, h - 1 - y)
        return 3 if d <= 1 else 0

    legal_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            legal_moves.append((dx, dy))
    if not legal_moves:
        return [0, 0]

    if not resources:
        # Go toward opponent's side but avoid adjacency: edge_patrol likes corners/edges
        best = legal_moves[0]
        bestv = -10**18
        for dx, dy in legal_moves:
            nx, ny = sx + dx, sy + dy
            v = -man(nx, ny, ox, oy) + edge_bonus(nx, ny)
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    best = legal_moves[0]
    bestv = -10**18
    # Evaluate each move by best resource swing + avoidance of giving opponent the tempo.
    for dx, dy in legal_moves:
        nx, ny = sx + dx, sy + dy
        best_my = 10**9
        best_op = 10**9
        target_dist_diff = 0
        # Compute: closest resource we can beat (or at least not lose badly).
        for rx, ry in resources:
            d_my = man(nx, ny, rx, ry)
            d_op = man(ox, oy, rx, ry)
            if d_my < best_my:
                best_my = d_my
                target_dist_diff = d_op - d_my
            # also allow a different resource with better advantage
            if (d_op - d_my) > target_dist_diff:
                target_dist_diff = d_op - d_my
        # Higher target_dist_diff means we are closer than opponent by more.
        # Also incorporate edge preference but only when it doesn't help opponent too much.
        # Penalty if we're close to opponent (prevents edge_patrol trapping).
        opp_pen = 0
        d_to_opp = man(nx, ny, ox, oy)
        if d_to_opp <= 1:
            opp_pen = 4
        v = 6 * target_dist_diff - 1.2 * best_my + edge_bonus(nx, ny) - opp_pen

        # If multiple resources are similarly good, bias toward the nearest resource directly.
        # (Deterministic due to fixed resource iteration order.)
        if target_dist_diff < 0:
            # We're behind somewhere; still pick move that minimizes our loss margin.
            # This encourages switching to a nearer-but-safe resource.
            v -= 3 * (-target_dist_diff)

        if v > bestv:
            bestv, best = v, (dx, dy)

    return [best[0], best[1]]