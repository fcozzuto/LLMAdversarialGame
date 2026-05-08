def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", [0, 0])
    ox, oy = int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    if not unclaimed and not self_t:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    dirs8 = moves
    best = None
    best_val = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        if (nx, ny) == (sx, sy) and (sx, sy) in blocked:
            continue

        base = 0
        if (nx, ny) in unclaimed:
            base += 4
        elif (nx, ny) in self_t:
            base += 1
        elif (nx, ny) in opp_t:
            base += 2  # flipping gains a cell; still prefer safer expansions
            base -= 2 if max(abs(nx - ox), abs(ny - oy)) <= 2 else 0

        # Local frontier pressure: prefer cells near unclaimed and away from opponent.
        frontier = 0
        self_n = 0
        opp_n = 0
        for ddx, ddy in dirs8:
            ax, ay = nx + ddx, ny + ddy
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) not in blocked:
                if (ax, ay) in unclaimed:
                    frontier += 1
                if (ax, ay) in self_t:
                    self_n += 1
                if (ax, ay) in opp_t:
                    opp_n += 1
        base += frontier * 1.2 + self_n * 0.2 - opp_n * 0.8

        # Deterministic tie-breaker: maximize distance to opponent slightly (safer growth).
        dist = max(abs(nx - ox), abs(ny - oy))
        val = base + dist * 0.05

        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]