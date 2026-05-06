def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obs

    def mdist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def near_obs_pen(x, y):
        # Small deterministic penalty to avoid hugging obstacles
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obs:
                    c += 1
        return c * 0.05

    if not resources:
        # Keep moving toward opponent direction with obstacle avoidance
        best = (0, 0)
        bestv = -1e9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = -mdist(nx, ny, ox, oy) - near_obs_pen(nx, ny)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_val = -1e18
    best_sd = 10**9

    # Prefer moves that create a winning distance margin to some resource (interception/steal).
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        sd = min(mdist(nx, ny, rx, ry) for rx, ry in resources)
        best_margin = -1e9
        for rx, ry in resources:
            selfd = mdist(nx, ny, rx, ry)
            oppd = mdist(ox, oy, rx, ry)
            margin = oppd - selfd
            # Extra preference when we'd be closer than opponent on that resource
            if margin > best_margin:
                best_margin = margin
        # Tie-break by faster access to closest resource and less obstacle hugging
        val = best_margin - 0.08 * sd - near_obs_pen(nx, ny)
        if val > best_val or (val == best_val and sd < best_sd):
            best_val = val
            best_sd = sd
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]