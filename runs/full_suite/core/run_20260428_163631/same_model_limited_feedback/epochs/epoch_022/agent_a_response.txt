def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs_set = {tuple(p) for p in obstacles}
    resources = observation.get("resources", [])
    if not resources:
        dx, dy = 0, 0
        opts = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        for step in opts:
            nx, ny = sx + step[0], sy + step[1]
            if (nx, ny) not in obs_set and 0 <= nx < w and 0 <= ny < h:
                dx, dy = step
                break
        return [dx, dy]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose resource to contest: favor low (our dist - opp dist)
    best = None
    best_val = None
    for rx, ry in resources:
        if (rx, ry) in obs_set:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        val = (ds - do, ds, -do, rx, ry)
        if best_val is None or val < best_val:
            best_val = val
            best = (rx, ry)
    tx, ty = best

    opts = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dxi, dyi in opts:
        nx, ny = sx + dxi, sy + dyi
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs_set:
            continue
        our_d = dist((nx, ny), (tx, ty))
        opp_d = dist((ox, oy), (tx, ty))
        # Small extra: if we land on a resource, strongly prefer it
        on_resource = 1 if (nx, ny) in {tuple(p) for p in resources} else 0
        # Blocking: also prefer moves that reduce our distance while increasing opponent's distance to us
        opp_to_us = dist((ox, oy), (nx, ny))
        score = (our_d, -opp_d, -on_resource, -opp_to_us, dxi, dyi)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dxi, dyi)

    # Deterministic fallback if somehow all moves invalid
    if best_score is None:
        return [0, 0]
    return [best_move[0], best_move[1]]