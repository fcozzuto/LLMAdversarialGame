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

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)
    def blocked(x, y): return (x, y) in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and not blocked(nx, ny):
            return [int(dx), int(dy)]
        for ddx, ddy in [(dx, 0), (0, dy), (0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)]:
            nx, ny = sx + ddx, sy + ddy
            if inb(nx, ny) and not blocked(nx, ny):
                return [int(ddx), int(ddy)]
        return [0, 0]

    best = None
    best_move = [0, 0]

    for ddx, ddy in moves:
        nx, ny = sx + ddx, sy + ddy
        if not inb(nx, ny) or blocked(nx, ny):
            continue

        # choose a target that we can reach sooner than opponent (denial-aware)
        # tie-break deterministically by coordinate sum then x,y
        chosen = None
        chosen_key = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            key = (2 * od - sd, -(sd), -(rx + ry), -rx, -ry)  # maximize denier advantage, then closer, then deterministic
            if chosen_key is None or key > chosen_key:
                chosen_key = key
                chosen = (rx, ry)

        rx, ry = chosen
        sd = man(nx, ny, rx, ry)
        od = man(ox, oy, rx, ry)

        # small preference to reduce immediate threat near opponent and avoid dead ends via obstacle adjacency
        adj_obs = 0
        for ax, ay in [(nx+1, ny), (nx-1, ny), (nx, ny+1), (nx, ny-1)]:
            if inb(ax, ay) and blocked(ax, ay):
                adj_obs += 1

        score = (2 * od - sd) - 0.1 * adj_obs
        if best is None or score > best:
            best = score
            best_move = [ddx, ddy]

    # if all candidate moves blocked (unlikely), stay
    if best is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]