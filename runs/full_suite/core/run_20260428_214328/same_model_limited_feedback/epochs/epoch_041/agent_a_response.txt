def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
        best = (None, -1e9)
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            # flee toward larger chebyshev distance to opponent
            dopp = max(abs(nx-ox), abs(ny-oy))
            if dopp > best[1]:
                best = ((dx, dy), dopp)
        return list(best[0]) if best[0] is not None else [0, 0]

    def cheb(a, b, c, d):
        return max(abs(a-c), abs(b-d))

    # Pick resource we can reach earlier (or steal), deterministically by scoring.
    best_t = None
    best_key = None
    for rx, ry in resources:
        dself = cheb(x, y, rx, ry)
        dopp = cheb(ox, oy, rx, ry)
        adv = dopp - dself
        key = (-adv, dself, cheb(0, 0, rx, ry), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_delta, best_score = None, -1e18
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        dist_t = cheb(nx, ny, tx, ty)
        dist_o = cheb(nx, ny, ox, oy)
        dself_now = cheb(x, y, tx, ty)
        dself_next = dist_t
        dopp = cheb(ox, oy, tx, ty)
        adv_next = dopp - dself_next
        score = (-dist_t * 2.0) + (adv_next * 0.8) + (dist_o * 0.02)
        # small deterministic tie-breaker toward lower dx/dy lexicographically
        score -= (0.001 * (dx + 2) + 0.0001 * (dy + 2))
        if score > best_score:
            best_score = score
            best_delta = (dx, dy)

    if best_delta is None:
        return [0, 0]
    return [int(best_delta[0]), int(best_delta[1])]