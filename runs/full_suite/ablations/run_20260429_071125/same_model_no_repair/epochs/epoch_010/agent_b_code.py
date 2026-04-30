def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = set((p[0], p[1]) for p in obstacles)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        d = abs(x1 - x2) + abs(y1 - y2)
        return d

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def obstacle_penalty(x, y):
        pen = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            if (x + dx, y + dy) in occ:
                pen += 1
        return pen

    if resources:
        best_target = None
        best_adv = None
        for rx, ry in resources:
            sd = dist(sx, sy, rx, ry)
            od = dist(ox, oy, rx, ry)
            adv = od - sd  # positive if we are closer
            key = (adv, -sd)  # tie-break: closer for us
            if best_adv is None or key > best_adv:
                best_adv = key
                best_target = (rx, ry)

        tx, ty = best_target
        # Evaluate candidate moves by improving our lead and keeping pressure.
        best_move = (0, 0)
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in occ:
                continue
            sd = dist(nx, ny, tx, ty)
            od = dist(ox, oy, tx, ty)
            adv_after = od - sd
            # Also discourage moving closer to opponent's nearest resource.
            opp_near = 10**9
            for rx, ry in resources:
                opp_near = min(opp_near, dist(ox, oy, rx, ry))
            val = adv_after * 80 - sd * 3 - obstacle_penalty(nx, ny) * 2 - dist(nx, ny, ox, oy) * 0.05
            # If opponent is closer, try to reduce the gap quickly.
            if adv_after < 0:
                val -= (-adv_after) * 30
            if val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No resources: drift toward center while avoiding obstacles.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in occ:
            continue
        val = -dist(nx, ny, cx, cy) - 0.1 * dist(nx, ny, ox, oy) - obstacle_penalty(nx, ny)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]