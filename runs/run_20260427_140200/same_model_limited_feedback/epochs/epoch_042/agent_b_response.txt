def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs_set = set((p[0], p[1]) for p in obstacles)
    occ_block = obs_set

    candidates = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        dx = 0
        dy = 0
        if sx < w-1 and sx >= 0: dx = 1
        if sy < h-1 and sy >= 0: dy = 1
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in occ_block:
            for ddx, ddy in candidates:
                nx, ny = sx + ddx, sy + ddy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in occ_block:
                    return [ddx, ddy]
        return [dx if 0 <= sx+dx < w else 0, dy if 0 <= sy+dy < h else 0]

    def d2(a, b):
        dx = a[0]-b[0]
        dy = a[1]-b[1]
        return dx*dx + dy*dy

    # Pick resource where we are (currently) most ahead; tie-break by closeness.
    best_t = None
    best_adv = -10**18
    for r in resources:
        rx, ry = r[0], r[1]
        if (rx, ry) in occ_block:
            continue
        adv = (d2((ox, oy), (rx, ry)) - d2((sx, sy), (rx, ry)))
        clos = d2((sx, sy), (rx, ry))
        if adv > best_adv or (adv == best_adv and clos < d2((sx, sy), (best_t[0], best_t[1])) if best_t else True):
            best_adv = adv
            best_t = (rx, ry)
    if best_t is None:
        best_t = (resources[0][0], resources[0][1])

    tx, ty = best_t
    # Evaluate candidate moves; maximize advantage to target and slightly avoid edges/obstacles.
    best_move = [0, 0]
    best_score = -10**18
    for ddx, ddy in candidates:
        nx, ny = sx + ddx, sy + ddy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in occ_block:
            continue
        self_dist = d2((nx, ny), (tx, ty))
        opp_dist = d2((ox, oy), (tx, ty))
        # Gain if we move closer than opponent relative position.
        score = (opp_dist - self_dist) * 3
        # Extra incentive to capture resources if adjacent/landing.
        if (nx, ny) in resources:
            score += 100000
        # Discourage moving into tight/blocked regions.
        block_pen = 0
        for ax, ay in candidates:
            px, py = nx + ax, ny + ay
            if px < 0 or px >= w or py < 0 or py >= h or (px, py) in occ_block:
                block_pen += 1
        score -= block_pen * 2
        # Slight bias to reduce distance to opponent when we are already close to target.
        if self_dist <= 4:
            score += d2((nx, ny), (ox, oy)) * -0.5
        if score > best_score:
            best_score = score
            best_move = [ddx, ddy]

    if best_score == -10**18:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]