def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation["resources"]; obstacles = set(tuple(p) for p in observation["obstacles"])
    # Chebyshev distance (diagonal allowed)
    def dist(a, b): 
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    # choose target resource where we're relatively closer than opponent
    best = None; best_score = -10**9; best_us = 10**9
    if resources:
        for rx, ry in resources:
            usd = dist((sx, sy), (rx, ry))
            opd = dist((ox, oy), (rx, ry))
            score = (opd - usd) * 10 - usd  # prioritize resources we can claim more than opp
            if score > best_score or (score == best_score and usd < best_us):
                best_score = score; best_us = usd; best = (rx, ry)
        tx, ty = best
    else:
        # fallback: go to center to deny space
        tx, ty = (w-1)//2, (h-1)//2

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    oppd_now = dist((sx, sy), (ox, oy))
    best_move = (0, 0); best_val = -10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_t = dist((nx, ny), (tx, ty))
        d_to_o = dist((nx, ny), (ox, oy))
        # If target is occupied by us next, strongly prefer
        on_target = 1 if (nx, ny) == (tx, ty) else 0
        # Prefer reducing distance to target; prefer increasing separation from opponent
        val = -d_to_t * 3 + d_to_o * 1.2 + on_target * 50
        # If opponent is very close, bias moving away
        if oppd_now <= 2:
            val += (d_to_o - oppd_now) * 4
        # small deterministic tie-break: lexicographic by move
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val; best_move = (dx, dy)
    dx, dy = best_move
    return [int(dx), int(dy)]