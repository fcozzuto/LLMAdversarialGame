def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def cheb(a, b, c, d):
        ax = a - c
        ay = b - d
        return (ax if ax >= 0 else -ax) if (ax if ax >= 0 else -ax) >= (ay if ay >= 0 else -ay) else (ay if ay >= 0 else -ay)

    # Pick a target resource by relative advantage over opponent (static per turn).
    best_res = None
    best_adv = -10**9
    if resources:
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = (do - ds)  # positive means we are closer
            # small tie-break: prefer closer overall to speed scoring
            adv = adv * 10 - ds
            if adv > best_adv:
                best_adv = adv
                best_res = (rx, ry)
    else:
        best_res = (sx, sy)

    tx, ty = best_res
    # If we're already on a resource, prefer to stay (deterministic collection).
    if (sx, sy) == (tx, ty) and resources:
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            val = -10**12
        else:
            ns = cheb(nx, ny, tx, ty)
            no = cheb(ox, oy, tx, ty)
            # maximize reduction in our distance; also slightly increase opponent distance
            val = -ns * 100 + no * 5
            # prefer moves that reduce distance while avoiding stepping into "dead-end" proximity to obstacles
            # by penalizing closeness to obstacles (chebyshev distance <=1)
            near_obs = 0
            if obstacles:
                for ox2, oy2 in ((nx-1, ny-1),(nx-1, ny),(nx-1, ny+1),(nx, ny-1),(nx, ny),(nx, ny+1),(nx+1, ny-1),(nx+1, ny),(nx+1, ny+1)):
                    if 0 <= ox2 < w and 0 <= oy2 < h and (ox2, oy2) in obstacles:
                        near_obs += 1
            val -= near_obs * 3
            # mild preference to avoid giving opponent immediate access to the target if we step away
            if resources:
                # if our move would make us not the closest, penalize
                cur_ds = cheb(nx, ny, tx, ty)
                cur_do = cheb(ox, oy, tx, ty)
                if cur_do <= cur_ds:
                    val -= 25
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]