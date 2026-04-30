def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs_set = set((a, b) for a, b in obstacles)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # No resources: drift toward center while avoiding obstacles.
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestv = -10**9
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs_set:
                nx, ny = x, y
            v = -cheb(nx, ny, tx, ty) - 0.2 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Pick a target resource that we are likely to reach first (relative to opponent).
    best_r = resources[0]
    best_r_score = 10**9
    for rx, ry in resources:
        md = cheb(x, y, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # If we're slower than opponent, penalize strongly; encourages a different target than last epoch.
        if md <= od:
            score = md
        else:
            score = md + 2.0 * (md - od) + 0.1 * cheb(rx, ry, (w - 1) // 2, (h - 1) // 2)
        if score < best_r_score:
            best_r_score = score
            best_r = (rx, ry)
    tr, ty = best_r

    # Evaluate each move by resulting position: choose the move that maximizes progress to target while managing opponent proximity.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs_set:
            nx, ny = x, y
            dx, dy = 0, 0
        md = cheb(nx, ny, tr, ty)
        od = cheb(ox, oy, tr, ty)
        dist_opp = cheb(nx, ny, ox, oy)
        # Prefer reducing distance to target; slight preference to keep some distance from opponent to avoid being punished.
        val = (-md) + 0.35 * (od - md) + 0.06 * dist_opp
        # Extra nudge to break ties toward moves that also reduce distance to target.
        cur_md = cheb(x, y, tr, ty)
        if val == best_val and md < cur_md:
            val += 1e-6
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move