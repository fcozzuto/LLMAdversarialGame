def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    steps = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    # Rank resources by our current race advantage (for tie-breaking and stability)
    rinfo = []
    for r in resources:
        sd = cheb((sx, sy), r)
        od = cheb((ox, oy), r)
        # higher means we are better positioned relative to opponent
        rinfo.append((od - sd, sd, od, r))
    rinfo.sort(reverse=True, key=lambda t: (t[0], -t[1], -t[2]))
    top = [t[3] for t in rinfo[:6]]  # keep evaluation small

    for dx, dy in steps:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Encourage becoming closer than opponent to contested resources; also pull toward opponent for interception.
        opp_step = cheb((ox, oy), (nx, ny))
        val = 0
        for r in top:
            sd_next = cheb((nx, ny), r)
            od = cheb((ox, oy), r)
            # If we can reach no later than opponent, strongly reward; otherwise penalize.
            race_gap = od - sd_next
            if race_gap >= 0:
                val += 1200 + 80 * race_gap - 5 * sd_next
            else:
                val += 50 * race_gap - 2 * sd_next
            # Small term to prefer reducing the immediate distance to opponent-held area.
            val -= 1.2 * opp_step
        # Deterministic tie-break: prefer moves that reduce our distance to the best currently-ranked resource.
        best_r = top[0]
        dcur = cheb((sx, sy), best_r)
        dfut = cheb((nx, ny), best_r)
        val -= 0.01 * (dfut - dcur)

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]