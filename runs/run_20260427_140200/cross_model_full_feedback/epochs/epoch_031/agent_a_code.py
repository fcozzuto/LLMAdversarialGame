def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dman(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def dcheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    best_dxdy = [0, 0]
    best_val = -10**18

    if resources:
        # Deterministically pick the neighbor that maximizes advantage for securing a resource.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            my_step_d = 0
            opp_threat = 0
            # Score: prefer states where some resource is closer to us than to opponent.
            # Favor larger advantage and also slightly prefer being closer overall.
            for rx, ry in resources:
                md = dcheb(nx, ny, rx, ry)
                od = dcheb(ox, oy, rx, ry)
                adv = od - md  # positive if we can reach sooner (or equal)
                # Encourage grabbing any nearby resource while discouraging giving opponent advantage.
                val = adv * 1000 - md - 3 * my_step_d
                # If opponent is already extremely close, still consider only if we are better.
                if adv >= 0:
                    val += 50
                if val > best_val:
                    best_val = val
                    best_dxdy = [dx, dy]
        return best_dxdy

    # No resources left: deterministic fallback—move to reduce distance to opponent cautiously.
    # (Mostly irrelevant if resources exist, but deterministic.)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        # Prefer moving toward center slightly while keeping distance from opponent.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dc = dcheb(nx, ny, cx, cy)
        do = dcheb(nx, ny, ox, oy)
        val = -do * 10 - dc
        if val > best_val:
            best_val = val
            best_dxdy = [dx, dy]
    return best_dxdy