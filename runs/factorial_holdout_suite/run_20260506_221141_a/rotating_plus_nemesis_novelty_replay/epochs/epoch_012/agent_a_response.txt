def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                res.append((rx, ry))

    if not res:
        return [0, 0]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def valid(x, y):
        return 0 <= x < gw and 0 <= y < gh and (x, y) not in obs

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Prefer moves that increase (opponent_time - self_time) to a resource, with short lookahead.
    best = (0, 0)
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        my_reachable = []
        for step in moves:
            nnx, nny = nx + step[0], ny + step[1]
            if valid(nnx, nny):
                my_reachable.append((nnx, nny))
        if not my_reachable:
            my_reachable = [(nx, ny)]

        sc = 0
        # For each resource, approximate your best pickup time in 1-2 moves, compare to opponent.
        for (rx, ry) in res:
            opp_t = dist(ox, oy, rx, ry)
            # Your time is either 1 move (if directly on/adjacent) or 2 via reachable set.
            self_t = 10**9
            for (px, py) in my_reachable:
                self_t = min(self_t, dist(px, py, rx, ry))
            # Convert to advantage; reward taking resources even if slightly slower when opponent is far.
            adv = opp_t - self_t
            if adv >= 0:
                sc += 20 + adv
            else:
                sc += adv  # still consider blocking/transitioning

        # Small tie-break: reduce distance to the single most contested resource (opponent closest).
        contested = min(res, key=lambda r: dist(ox, oy, r[0], r[1]))
        sc -= dist(nx, ny, contested[0], contested[1]) * 0.01

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)
    return [int(best[0]), int(best[1])]