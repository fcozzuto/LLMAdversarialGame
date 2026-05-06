def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]

    obs_set = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]

    if not resources:
        cx, cy = w // 2, h // 2
        best = [0, 0]
        bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            v = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) - 0.01 * (abs(nx - ox) + abs(ny - oy))
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    def d2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Choose a target resource emphasizing "win-the-race": maximize (opp_dist - self_dist)
    # If all are losing races, go toward the closest resource to reduce loss.
    best_resource = None
    best_res_score = -10**18
    for rx, ry in resources:
        sd = d2(sx, sy, rx, ry)
        od = d2(ox, oy, rx, ry)
        race = (od - sd)  # positive means we are closer (in squared distance)
        # small bias to higher "spatial spread" (discourage local traps)
        spread = (rx + ry) * 0.0
        score = race + 0.01 * spread
        if score > best_res_score:
            best_res_score = score
            best_resource = (rx, ry)

    # If opponent is closer to everything (all race scores negative), switch to nearest resource to self
    if best_res_score < 0:
        best_resource = min(resources, key=lambda r: d2(sx, sy, r[0], r[1]))

    rx, ry = best_resource

    # Evaluate next move: win-the-race for that target plus obstacle proximity repulsion and opponent avoidance.
    best = [0, 0]
    bestv = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue

        sd_next = d2(nx, ny, rx, ry)
        od = d2(ox, oy, rx, ry)
        race_next = (od - sd_next)

        # Repel from obstacles to avoid getting stuck near corners/blocks
        rep = 0
        for ax, ay in obstacles:
            t = abs(nx - ax) + abs(ny - ay)
            if t <= 1:
                rep -= 20
            elif t <= 2:
                rep -= 5
        # Mild avoidance of opponent to prevent sharing contested routes
        opp_avoid = -0.05 * d2(nx, ny, ox, oy)

        # Encourage progress toward target (avoid oscillation)
        progress = -0.001 * (d2(nx, ny, sx, sy))

        v = race_next + rep + opp_avoid + progress
        if v > bestv:
            bestv = v
            best = [dx, dy]

    return [int(best[0]), int(best[1])]