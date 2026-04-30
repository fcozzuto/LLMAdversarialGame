def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    neigh = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx*dx + dy*dy)

    best = None
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        opp_d = dist((nx, ny), (ox, oy))
        move_pen = 0
        if opp_d <= 4:  # avoid getting too close
            move_pen += 20
        if opp_d <= 1:
            move_pen += 50

        # choose best target resource from this hypothetical position
        if not resources:
            # fallback: move away from opponent to avoid conflict
            # pick direction that maximizes distance to opponent
            val = -opp_d + move_pen
        else:
            val = None
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                myd = dist((nx, ny), (rx, ry))
                opd = dist((ox, oy), (rx, ry))
                # Prefer resources where we are closer than opponent; also prefer shorter myd
                # Deterministic tie-breaking via additional terms.
                advantage = (opd - myd)
                # Obstacle proximity heuristic: discourage stepping near obstacles
                obs_adj = 0
                for ax in (rx-1, rx, rx+1):
                    for ay in (ry-1, ry, ry+1):
                        if (ax, ay) in obstacles:
                            obs_adj += 1
                score = -advantage + myd*0.15 + obs_adj*0.1
                # Slight bias to earlier (x,y) deterministically when equal
                score += (rx * 0.0001 + ry * 0.00001)
                if val is None or score < val:
                    val = score
            val = val + move_pen

        if best is None or val < best[0]:
            best = (val, [dx, dy])

    if best is None:
        return [0, 0]
    return [best[1][0], best[1][1]]