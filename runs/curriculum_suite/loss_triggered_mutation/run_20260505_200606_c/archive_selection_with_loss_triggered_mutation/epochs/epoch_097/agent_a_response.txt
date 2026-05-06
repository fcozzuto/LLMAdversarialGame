def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                res.append((rx, ry))
    res.sort()

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_val = None

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Score this next state by trying to pick a resource we can reach before opponent.
        state_best = None
        for rx, ry in res:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Reach race: prefer positive (we are closer), strongly avoid where opponent is much closer.
            race = od - sd
            # Small deterministic tiebreakers to reduce oscillation.
            tie = (rx + 3 * ry) % 9
            val = -1000 * (race < 0) - 20 * (race < 1) + 3 * race - sd - 0.01 * tie
            if state_best is None or val > state_best:
                state_best = val
        if state_best is None:
            # If no resources, just stay deterministic
            state_best = -man(nx, ny, w - 1, h - 1)

        if best_val is None or state_best > best_val:
            best_val = state_best
            best_move = (dx, dy)
        elif best_val is not None and state_best == best_val:
            # Deterministic tie-break
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]