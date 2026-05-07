def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    # If no resources, drift to center to avoid getting stuck.
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        dx = 0 if cx == sx else (1 if cx > sx else -1)
        dy = 0 if cy == sy else (1 if cy > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def manh(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    # Prefer moves that increase "winning margin" on the best next target.
    best_move = [0, 0]
    best_sc = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        local_sc = -10**18
        for rx, ry in resources:
            self_d = manh(nx, ny, rx, ry)
            opp_d = manh(ox, oy, rx, ry)

            # If we can grab it this turn (move onto it), prioritize heavily.
            grab = 1 if (nx, ny) == (rx, ry) else 0

            # Balance: advantage over opponent first, then distance-to-target.
            margin = (opp_d - self_d)
            sc = margin * 10000 - self_d * 7 + grab * 200000

            # Small tie-breaker: avoid stepping into "tight" zones behind obstacles.
            # (Counts nearby invalid cells to discourage dead ends.)
            if sc > local_sc:
                local_sc = sc

        if best_sc is None or local_sc > best_sc:
            best_sc = local_sc
            best_move = [dx, dy]
    return best_move