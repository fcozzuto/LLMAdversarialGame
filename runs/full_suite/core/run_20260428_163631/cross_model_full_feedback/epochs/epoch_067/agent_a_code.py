def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def adj_obs_pen(x, y):
        pen = 0
        for ax in (x-1, x, x+1):
            for ay in (y-1, y, y+1):
                if (ax, ay) in obstacles:
                    pen += 2
        return pen

    def opp_can_block(nx, ny):
        return md(ox, oy, nx, ny) <= 1

    best = None
    best_val = None
    for dx, dy, nx, ny in legal:
        if resources:
            val = -10**9
            for rx, ry in resources:
                ds = md(nx, ny, rx, ry)
                do = md(ox, oy, rx, ry)
                adv = do - ds  # being closer than opponent is good
                # small preference for reducing our distance once advantage exists
                near = -ds * 0.1 - (0.05 * (ds == 0))
                # avoid moving toward positions where opponent can immediately contest
                contest = -4.0 if opp_can_block(nx, ny) else 0.0
                # obstacle adjacency penalty
                obs_pen = -adj_obs_pen(nx, ny) * 0.6
                v = adv + near + contest + obs_pen
                if v > val:
                    val = v
        else:
            # No resources visible: go for opponent side while avoiding obstacles
            target_x = w - 1 if ox < w//2 else 0
            target_y = h - 1 if oy < h//2 else 0
            val = -md(nx, ny, target_x, target_y) - adj_obs_pen(nx, ny) * 0.6 - (2.0 if opp_can_block(nx, ny) else 0.0)

        # tie-break deterministically: prefer moves with smallest dx, then dy, then staying
        if best_val is None or val > best_val or (val == best_val and (best is None or (dx, dy) < best)):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]