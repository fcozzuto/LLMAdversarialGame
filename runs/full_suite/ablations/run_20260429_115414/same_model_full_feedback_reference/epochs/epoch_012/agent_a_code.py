def choose_move(observation):
    W = observation["grid_width"]; H = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    res = []
    seen = set()
    for p in resources:
        if p and len(p) >= 2:
            t = (p[0], p[1])
            if t not in obs and t not in seen:
                seen.add(t); res.append(t)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < W and 0 <= y < H
    def legal(x, y): return inb(x, y) and (x, y) not in obs
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    rset = set(res)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny) and (nx, ny) in rset:
            return [dx, dy]

    if not res:
        best = (0, 0); bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0); best_val = -10**18
    # Evaluate moves by best achievable "advantage" over opponent for any remaining resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Deterministic: iterate resources in fixed order.
        cur_best = -10**18
        for rx, ry in res:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer; break ties by pushing toward the target.
            # Also give slight incentive to avoid becoming much farther than current.
            cur_best = max(cur_best, (opp_d - my_d) * 1000 - my_d)
        if cur_best > best_val:
            best_val = cur_best; best_move = (dx, dy)

    return [best_move[0], best_move[1]]