def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def md(a, b, c, d):
        # Chebyshev distance works well with 8-direction moves
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    if resources:
        best_res = resources[0]
        best_res_score = -10**18
        for rx, ry in resources:
            ds = md(sx, sy, rx, ry)
            do = md(ox, oy, rx, ry)
            # Prefer resources that are closer to us than opponent
            sc = (do - ds) * 1000 - ds
            # Also bias toward generally reachable resources
            sc += (rx + ry) * 2  # deterministic tie-break
            if sc > best_res_score:
                best_res_score = sc
                best_res = (rx, ry)
        tr, ty = best_res
    else:
        tr, ty = (w - 1 - sx, h - 1 - sy)

    # Evaluate next step: move closer to target and avoid stepping into tight obstacle neighborhoods.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist_to_target = md(nx, ny, tr, ty)
        # Prefer decreasing distance to target (implicitly greedy)
        val = -dist_to_target * 10
        # If target is on this tile, add big reward
        if nx == tr and ny == ty:
            val += 10**6
        # Penalize closeness to obstacles (to reduce trapping)
        near_obs = 0
        for ox2 in (-1, 0, 1):
            for oy2 in (-1, 0, 1):
                if ox2 == 0 and oy2 == 0:
                    continue
                tx, ty2 = nx + ox2, ny + oy2
                if (tx, ty2) in obstacles:
                    near_obs += 1
        val -= near_obs * 3
        # Head-off opponent: prefer tiles where we are at least not further than opponent to the target
        opp_dist = md(ox, oy, tr, ty)
        our_future = dist_to_target
        val += (opp_dist - our_future) * 2
        # Deterministic tie-break
        val += (dx + 1) * 0.001 + (dy + 1) * 0.0001
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]