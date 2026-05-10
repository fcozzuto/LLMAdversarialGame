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

    t = int(observation.get("turn_index", 0))
    opp_list = list(opp)
    un_list = list(unclaimed)

    def nearest_dist(pt_list, nx, ny, fallback=10**9):
        if not pt_list:
            return fallback
        dmin = 10**9
        for px, py in pt_list:
            d = abs(px - nx) + abs(py - ny)
            if d < dmin:
                dmin = d
        return dmin

    best_val = -10**18
    best = [0, 0]
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            val = -10**18
        else:
            val = 0
            if (nx, ny) in opp:
                val += 1000  # immediate flip opportunity
            if (nx, ny) in unclaimed:
                val += 120  # expanding into neutral
            if (nx, ny) in selft:
                val += 10  # maintain
            # Move toward opponent territory if we can flip, else toward unclaimed
            if (nx, ny) in opp:
                val += 5 * (8 - nearest_dist(opp_list, nx, ny, 0))
            else:
                val += 3 * (8 - nearest_dist(un_list, nx, ny, 0))
            # Prefer staying away from obstacles "pressure" by penalizing moves adjacent to obstacles
            adj_obs = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    if inb(nx + ax, ny + ay) and (nx + ax, ny + ay) in obs:
                        adj_obs += 1
            val -= 2 * adj_obs
            # Deterministic tie-break: small parity term
            val += 0.001 * ((nx + ny + t) & 7)

        if val > best_val:
            best_val = val
            best = [dx, dy]
    return best