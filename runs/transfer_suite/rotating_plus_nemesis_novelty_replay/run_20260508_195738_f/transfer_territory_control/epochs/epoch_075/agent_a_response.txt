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
    best = -10**18
    best_move = [0, 0]

    def inb(nx, ny): return 0 <= nx < w and 0 <= ny < h

    opp_list = list(opp)
    def dist_to_nearest_opp(nx, ny):
        if not opp_list: return 10**6
        md = 10**6
        for px, py in opp_list:
            d = abs(px - nx) + abs(py - ny)
            if d < md: md = d
        return md

    def adjacent_to_opp(nx, ny):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                if (nx + dx, ny + dy) in opp:
                    return True
        return False

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obs: 
            continue

        if (nx, ny) in opp:
            score = 500.0  # flipping is valuable
        elif (nx, ny) in unclaimed:
            score = 120.0
        elif (nx, ny) in selft:
            score = 50.0
        else:
            score = 10.0

        if adjacent_to_opp(nx, ny):
            score += 80.0

        score += max(0, 35 - dist_to_nearest_opp(nx, ny))  # approach opponent if possible

        # Nudge away from obstacles by penalizing moves that are "crowded" by obstacles
        crowd = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0: 
                    continue
                cx, cy = nx + ax, ny + ay
                if inb(cx, cy) and (cx, cy) in obs:
                    crowd += 1
        score -= 8.0 * crowd

        if score > best:
            best = score
            best_move = [dx, dy]

    return best_move