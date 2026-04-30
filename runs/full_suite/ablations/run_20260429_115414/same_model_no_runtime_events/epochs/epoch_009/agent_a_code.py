def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        res = []

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def safe(x, y): return inb(x, y) and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Tie-break deterministically by (value, -dist_to_opponent, next_pos)
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue

        # Prefer blocking: if we can get to a resource no later than opponent, value it strongly.
        if res:
            bestv = -10**18
            for rx, ry in sorted(res, key=lambda t: (t[0], t[1])):
                dm = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # If we can arrive earlier or tie, big reward; otherwise penalize.
                advantage = do - dm
                # Also keep pressure to actually reach quickly.
                v = 0
                if advantage >= 0:
                    v += 8000 * (advantage + 1)  # decisive
                    v += 50 * (10 - dm) if dm < 10 else -2 * dm
                else:
                    v += 120 * advantage - 5 * dm  # still progress
                # slight penalty for being far from any resource (encourages commitment)
                v -= 0.2 * cheb(nx, ny, ox, oy)
                if v > bestv:
                    bestv = v
            val = bestv
        else:
            # No resources known: drift toward center while not walking into obstacles.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            dc = cheb(nx, ny, int(cx), int(cy))
            val = -dc - 0.1 * cheb(nx, ny, ox, oy)

        # Extra deterministic bias to avoid oscillation: prefer moves that reduce distance to chosen resource
        # and prefer non-staying unless tie.
        dist_op = cheb(nx, ny, ox, oy)
        stay_pen = 1 if (dx == 0 and dy == 0) else 0
        key = (val - 0.01 * dist_op - 2 * stay_pen, -dist_op, nx, ny)
        if best is None or key > best:
            best = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]