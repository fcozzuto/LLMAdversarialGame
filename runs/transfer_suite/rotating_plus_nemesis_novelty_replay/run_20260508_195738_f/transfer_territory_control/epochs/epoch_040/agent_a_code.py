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

    def min_dist_to_set(nx, ny, s):
        if not s:
            return 10**9
        md = 10**9
        for px, py in s:
            d = abs(px - nx) + abs(py - ny)
            if d < md:
                md = d
        return md

    # Build "frontier" targets: unclaimed cells adjacent (8-neigh) to opponent territory
    frontier = set()
    if opp:
        for ux, uy in unclaimed:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    if (ux + dx, uy + dy) in opp:
                        frontier.add((ux, uy))
                        dx = dy = 2
                        break
                else:
                    continue
                break

    targets = frontier if frontier else unclaimed

    opp_cells = list(opp) if opp else None
    best_val = -10**18
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        landing_gain = 0
        if (nx, ny) in opp:
            landing_gain = 6
        elif (nx, ny) in unclaimed:
            landing_gain = 3
        elif (nx, ny) in selft:
            landing_gain = 0
        else:
            landing_gain = 1  # likely other neutral area (still claims)

        # Prefer moves that reduce distance to opponent territory (and to frontier if available)
        dist_opp = min_dist_to_set(nx, ny, opp) if opp_cells is not None else 10**6
        dist_tgt = 0
        if targets:
            dist_tgt = min_dist_to_set(nx, ny, targets)

        val = (landing_gain * 1000) - (dist_opp * 4) - (dist_tgt * 1)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move