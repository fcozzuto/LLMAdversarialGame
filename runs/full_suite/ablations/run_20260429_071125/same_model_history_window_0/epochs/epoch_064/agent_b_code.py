def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation["resources"]; obstacles = set(tuple(p) for p in observation["obstacles"])
    opts = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # choose best resource to aim for: maximize (opp_distance - self_distance) from next position
    best_move = (0, 0); best_score = -10**9

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist2(a, b):
        dx = a[0] - b[0]; dy = a[1] - b[1]
        return dx*dx + dy*dy

    if not resources:
        # fallback: head toward opponent's side (diagonal toward their corner)
        tx = w - 1 if ox < w/2 else 0
        ty = h - 1 if oy < h/2 else 0
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    # Precompute "best target" from current for tie-breaking
    cur_best_res = resources[0]
    cur_best_val = -10**18
    for r in resources:
        v = dist2((ox, oy), r) - dist2((sx, sy), r)
        if v > cur_best_val:
            cur_best_val = v; cur_best_res = r

    for dx, dy in opts:
        nsx, nsy = sx + dx, sy + dy
        if not valid(nsx, nsy):  # if invalid, engine would keep position; treat as worse
            continue
        local_best = -10**18
        local_res = resources[0]
        for r in resources:
            self_d = dist2((nsx, nsy), r)
            opp_d = dist2((ox, oy), r)
            # prefer landing on resource strongly; slight tie-break toward center
            center_bonus = -((nsx - (w-1)/2)**2 + (nsy - (h-1)/2)**2) * 0.0001
            score = (opp_d - self_d) + (200000 if self_d == 0 else 0) + center_bonus
            if score > local_best:
                local_best = score; local_res = r
        # tie-break: if same local_best, prefer move that also matches current best resource
        tie = 0
        if local_res == cur_best_res:
            tie = 0.01
        if local_best + tie > best_score:
            best_score = local_best + tie
            best_move = (dx, dy)

    # If all moves invalid (unlikely), stay
    return [int(best_move[0]), int(best_move[1])]