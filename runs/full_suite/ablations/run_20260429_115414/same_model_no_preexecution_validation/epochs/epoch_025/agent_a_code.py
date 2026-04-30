def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))

    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in obs

    res = []
    for r in resources:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obs_clear_bonus(x, y):
        # Prefer moving to more open area (deterministic local scan)
        b = 0
        for ax in (x-1, x, x+1):
            for ay in (y-1, y, y+1):
                if (ax, ay) in obs:
                    b -= 1
        return -b  # higher is better

    best = None
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        if res:
            d_self = min(cheb(nx, ny, rx, ry) for rx, ry in res)
            d_opp = min(cheb(ox, oy, rx, ry) for rx, ry in res)
        else:
            d_self = 0
            d_opp = 0

        # If we can reach a resource no later than opponent, prioritize that.
        reach_adv = (d_opp - d_self)  # positive favors us
        # Also keep distance from opponent to reduce contest probability.
        dist_from_opp = cheb(nx, ny, ox, oy)

        val = (reach_adv * 100.0) + (dist_from_opp * 2.0) - (d_self * 1.0) + (obs_clear_bonus(nx, ny) * 0.5)

        # Deterministic tie-break: prefer smaller dx, then smaller dy, then staying closer to resources by val recompute
        key = (val, -abs(dx), -abs(dy), -d_self, dist_from_opp, dx, dy)
        if best is None or key > best:
            best = key
            best_val = val

    if best is None:
        return [0, 0]
    # Extract move from iteration using same tie logic deterministically
    # Since we didn't store move, recompute best move with same ordering.
    best_moves = []
    target_val = best_val
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if res:
            d_self = min(cheb(nx, ny, rx, ry) for rx, ry in res)
            d_opp = min(cheb(ox, oy, rx, ry) for rx, ry in res)
        else:
            d_self = 0
            d_opp = 0
        reach_adv = (d_opp - d_self)
        dist_from_opp = cheb(nx, ny, ox, oy)
        val = (reach_adv * 100.0) + (dist_from_opp * 2.0) - (d_self * 1.0) + (obs_clear_bonus(nx, ny) * 0.5)
        if val > target_val - 1e-9 and val < target_val + 1e-9:
            best_moves.append((dx, dy))
    # Choose deterministically: prefer (0,0), then lexicographically smallest by dx,dy
    if (0, 0) in best_moves:
        return [0, 0]
    best_moves.sort()
    return [int(best_moves[0][0]), int(best_moves[0][1])]