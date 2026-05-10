def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def blocked(x, y):
        return (x, y) in obs

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and not blocked(nx, ny):
            return [dx, dy]
        # fallback: nearest axis direction that is valid
        for ddx, ddy in [(dx, 0), (0, dy), (0, 0)]:
            nx, ny = sx + ddx, sy + ddy
            if inb(nx, ny) and not blocked(nx, ny):
                return [ddx, ddy]
        return [0, 0]

    # For each possible move, pick the one that maximizes our best lead to any resource.
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        self_d = [man(nx, ny, int(r[0]), int(r[1])) for r in resources]
        opp_d = [man(ox, oy, int(r[0]), int(r[1])) for r in resources]
        # primary: maximum (opp_dist - self_dist); secondary: smallest self_dist; tertiary: deterministic hash tie-break
        lead = -10**9
        min_sd = 10**9
        hsum = 0
        for r, sd, od in zip(resources, self_d, opp_d):
            if od - sd > lead:
                lead = od - sd
            if sd < min_sd:
                min_sd = sd
            rx, ry = int(r[0]), int(r[1])
            hsum = (hsum * 131 + (rx * 17 + ry)) % 1000003
        cand = (lead, -min_sd, -hsum)
        if best_val is None or cand > best_val:
            best_val = cand
            best_move = (dx, dy)

    if best_move == (0, 0):
        # deterministic fallback if all moves blocked: try stay or minimal valid move
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]