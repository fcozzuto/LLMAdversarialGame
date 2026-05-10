def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def neighbors(nx, ny):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ax, ay = nx + dx, ny + dy
                if inb(ax, ay):
                    yield ax, ay

    def min_manh_to_set(nx, ny, s):
        if not s:
            return 10**9
        md = 10**9
        for (px, py) in s:
            d = abs(px - nx) + abs(py - ny)
            if d < md:
                md = d
        return md

    opp_list = list(opp)
    best = (-(10**18), 0, 0)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        val = 0.0
        if (nx, ny) in opp:
            val += 120.0  # direct counter-claim value
        if (nx, ny) in unclaimed:
            val += 35.0
        if (nx, ny) in selft:
            val += 6.0

        # Frontier pressure: prefer cells adjacent to opponent or unclaimed
        adj_opp = 0
        adj_un = 0
        for ax, ay in neighbors(nx, ny):
            if (ax, ay) in opp:
                adj_opp += 1
            if (ax, ay) in unclaimed:
                adj_un += 1
        val += 10.0 * adj_opp + 4.0 * adj_un

        # Distance shaping: head toward opponent, but not at the cost of immediate flip/claim
        if opp_list:
            val += 0.8 * (-min_manh_to_set(nx, ny, opp))

        # Mild penalty if we step away from our own territory too much (reduce counterclaim vulnerability)
        if selft:
            val += 0.2 * (-min_manh_to_set(nx, ny, selft))

        cand = (val, dx, dy)
        if cand > best:
            best = cand

    return [best[1], best[2]]