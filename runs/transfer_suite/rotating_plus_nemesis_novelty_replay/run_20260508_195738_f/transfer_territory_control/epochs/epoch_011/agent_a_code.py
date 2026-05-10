def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory") or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells") or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    opp_list = list(opp)
    def inb(a, b): return 0 <= a < w and 0 <= b < h
    def min_manh_to_opp(a, b):
        if not opp_list:
            return 10**6
        md = 10**6
        for ox, oy in opp_list:
            d = abs(ox - a) + abs(oy - b)
            if d < md:
                md = d
        return md

    def neighbor_has(a, b, s):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (a + dx, b + dy) in s:
                    return True
        return False

    best = -10**18
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        val = 0.0
        if (nx, ny) in unclaimed:
            val += 4.0
        elif (nx, ny) in selft:
            val += 1.0
        elif (nx, ny) in opp:
            val += 6.0

        if (nx, ny) in opp:
            val += 2.0

        if neighbor_has(nx, ny, opp):
            val += 1.5

        d = min_manh_to_opp(nx, ny)
        val += max(0.0, 6.0 - d) * 0.35

        # Deterministic tie-break: prefer moving over staying, then lexicographic by (dx,dy)
        if val > best or (val == best and (dx != 0 or dy != 0 or (dx, dy) < best_move)):
            best = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]