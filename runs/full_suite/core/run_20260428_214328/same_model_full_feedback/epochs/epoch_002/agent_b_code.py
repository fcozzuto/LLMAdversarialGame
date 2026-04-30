def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = [tuple(p) for p in observation.get("resources", [])]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    inf = 10**9

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        # Target a resource where we are advantaged (opp closer => harder, opp farther => easier).
        best_r = None
        best_key = None
        for r in resources:
            dself = cheb((sx, sy), r)
            dopp = cheb((ox, oy), r)
            # Prefer large advantage; break ties by choosing closer to us.
            key = (dopp - dself, -dself, -r[0], -r[1])
            if best_key is None or key > best_key:
                best_key = key
                best_r = r
        tx, ty = best_r

    # Obstacle distance helper
    def min_obs_dist(x, y):
        md = inf
        for (ax, ay) in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < md:
                md = d
        return 0 if md == inf else md

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dself = cheb((nx, ny), (tx, ty))
        dobb = cheb((ox, oy), (tx, ty))

        # Encourage closing on target and discouraging approaching opponent (when target is contested).
        contested = 1 if dobb - dself <= 2 else 0
        dist_opp_after = cheb((nx, ny), (ox, oy))

        # Favor staying away from obstacles.
        obs_pen = 0
        od = min_obs_dist(nx, ny)
        if od <= 1:
            obs_pen = 3
        elif od <= 2:
            obs_pen = 1

        # Value: higher is better
        val = (dobb - dself, -dself, -contested * dist_opp_after, -dx * 0 - dy * 0, -obs_pen)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]