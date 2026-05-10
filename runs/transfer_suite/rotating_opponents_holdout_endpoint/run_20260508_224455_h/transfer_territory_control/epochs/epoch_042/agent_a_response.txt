def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for c in (observation.get("obstacles", []) or []):
        if c is None:
            continue
        obstacles.add((int(c[0]), int(c[1])))

    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells", []) or []))
    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory", []) or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory", []) or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    opp_list = list(opp_terr)
    un_list = list(unclaimed)

    def manh(a, b, c, d): return abs(a - c) + abs(b - d)

    best_move = (0, 0)
    best_val = -10**18

    # Precompute nearest targets (cheap, deterministic sampling)
    def nearest_dist_to_set(x, y, S, limit=10):
        if not S:
            return 999
        if len(S) <= limit:
            return min(manh(x, y, p[0], p[1]) for p in S)
        # deterministic: take first 'limit' entries
        m = 999
        for i in range(limit):
            p = S[i]
            d = manh(x, y, p[0], p[1])
            if d < m:
                m = d
        return m

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Base gain for immediate control change
        if (nx, ny) in self_terr:
            gain = 1
        elif (nx, ny) in unclaimed:
            gain = 4
        elif (nx, ny) in opp_terr:
            gain = 7  # flipping on entry is enabled
        else:
            gain = 0

        # Positioning: drift towards center and towards attack targets
        d_center = manh(nx, ny, cx, cy)
        d_opp = manh(nx, ny, ox, oy)

        d_un = nearest_dist_to_set(nx, ny, un_list, limit=12)
        d_oppterr = nearest_dist_to_set(nx, ny, opp_list, limit=12)

        # Opportunistic: if adjacent to opponent territory, prioritize capture
        near_opp = 1 if d_oppterr == 0 else 0
        adj_opp = 1 if d_oppterr == 1 else 0

        # Defensive nudge: don't walk into deep opponent territory expansion too slowly
        # (push away from opponent when gains are equal)
        val = 0
        val += gain * 100
        val += (16 - d_center) * 2
        val += (20 - d_un) * 1.5
        val += (25 - d_oppterr) * 2.0
        val += adj_opp * 30 + near_opp * 50
        val += (-d_opp) * 0.3

        # Deterministic tie-break: prefer move that changes x/y earlier in list order
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]