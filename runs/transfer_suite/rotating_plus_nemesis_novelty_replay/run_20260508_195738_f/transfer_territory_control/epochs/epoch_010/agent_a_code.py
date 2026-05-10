def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(a, b): return 0 <= a < w and 0 <= b < h

    opp_list = list(opp)
    def min_manh(a, b):
        if not opp_list:
            return 10**9
        md = 10**9
        for ox, oy in opp_list:
            d = abs(ox - a) + abs(oy - b)
            if d < md: md = d
        return md

    def near_count(a, b, s):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (a + dx, b + dy) in s:
                    c += 1
        return c

    best = (-10**18, 10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        val = 0
        if (nx, ny) in unclaimed:
            val += 3
        elif (nx, ny) in opp:
            val += 6
        elif (nx, ny) in selft:
            val += 1

        val += near_count(nx, ny, opp) * 1.5
        val += near_count(nx, ny, unclaimed) * 0.3

        if (nx, ny) in opp:
            val += 1.0  # ensure capture is prioritized
        dOpp = min_manh(nx, ny)
        dSelf = min_manh(nx, ny) if not selft else 0  # keep deterministic, harmless

        cand = (val, -dOpp, dx, dy)
        if cand > best:
            best = cand

    return [best[2], best[3]]