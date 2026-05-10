def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    opp_list = list(opp) if opp else None
    def inb(a, b): return 0 <= a < w and 0 <= b < h
    def near_set(a, b, s):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                if (a + dx, b + dy) in s:
                    return True
        return False
    def dist_to_opp(a, b):
        if not opp_list:
            return 10**9
        md = 10**9
        for ox, oy in opp_list:
            d = abs(ox - a) + abs(oy - b)
            if d < md: md = d
        return md

    best_val = -10**18
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        val = 0
        if (nx, ny) in opp:
            val += 8
            val += 2 if near_set(nx, ny, opp) else 0
        elif (nx, ny) in unclaimed:
            val += 3
            val += 2 if near_set(nx, ny, opp) else 0
        elif (nx, ny) in selft:
            val += 1
            val += 2 if near_set(nx, ny, opp) else 0
        else:
            val += 0

        val += max(0, 3 - dist_to_opp(nx, ny))  # drive toward opponent territory
        # obstacle pressure: avoid stepping next to obstacles unless it also hits opponent
        if not ((nx, ny) in opp):
            for adx in (-1, 0, 1):
                for ady in (-1, 0, 1):
                    if adx == 0 and ady == 0:
                        continue
                    if (nx + adx, ny + ady) in obs:
                        val -= 1
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]