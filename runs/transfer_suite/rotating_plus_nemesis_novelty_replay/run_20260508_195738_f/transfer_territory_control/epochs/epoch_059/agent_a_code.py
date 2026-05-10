def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs_cells = set((p[0], p[1]) for p in obstacles)
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(nx, ny): return 0 <= nx < w and 0 <= ny < h

    opp_list = list(opp)
    def nearest_opp_dist(nx, ny):
        if not opp_list: return 10**6
        dmin = 10**9
        for px, py in opp_list:
            d = abs(px - nx) + abs(py - ny)
            if d < dmin: dmin = d
        return dmin

    def adj_opp(nx, ny):
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0: continue
                ax, ay = nx + ddx, ny + ddy
                if (ax, ay) in opp: return True
        return False

    # Prefer (1) cells adjacent to opponent territory, (2) unclaimed/neutral cells,
    # (3) avoiding obstacles, (4) slight bias to expand outward from current territory.
    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny): continue
        if (nx, ny) in obs_cells: continue

        on_self = (nx, ny) in selft
        is_un = (nx, ny) in unclaimed
        into_opp = (nx, ny) in opp
        near = nearest_opp_dist(nx, ny)
        touching = adj_opp(nx, ny)

        score = 0
        if touching: score += 60
        if into_opp: score += 120  # flipping on entry
        if is_un: score += 25
        if on_self: score += 10

        # Encourage moving toward the closest opponent boundary early, less later.
        t = int(observation.get("turn_index", 0))
        focus = 1.0 if t < 40 else 0.6
        score += int(30 * focus / (1 + near))

        # Small penalty for stepping into squares that are "too close" to obstacles isn't needed;
        # obstacle moves are prevented by staying put in engine, but we already filtered.
        if score > best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]