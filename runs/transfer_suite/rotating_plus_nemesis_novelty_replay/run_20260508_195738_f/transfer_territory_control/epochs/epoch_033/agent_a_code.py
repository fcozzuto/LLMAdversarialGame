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

    opp_list = list(opp)
    self_list = list(selft)

    def min_dist(pt, pts):
        if not pts:
            return 10**9
        px, py = pt
        md = 10**9
        for qx, qy in pts:
            d = abs(qx - px) + abs(qy - py)
            if d < md:
                md = d
        return md

    def score_cell(nx, ny):
        if (nx, ny) in obs:
            return -10**12
        d_opp = min_dist((nx, ny), opp_list)
        if (nx, ny) in opp:
            return -10**8 + 3 * d_opp  # avoid counterclaim/flip unless very safe (rare)
        s = 0
        if (nx, ny) in selft:
            s += 50 + 2 * d_opp
        if (nx, ny) in unclaimed:
            s += 30 + 3 * d_opp
            s += 6 - min_dist((nx, ny), self_list)  # prefer expanding from our presence
        else:
            # neutral/unknown squares: lightly prefer staying closer to our territory while far from opponent
            s += 4 - min_dist((nx, ny), self_list)
            s += 1 * d_opp
        # encourage moving away from opponent if ahead/behind slightly
        if observation.get("self_territory_count", 0) >= observation.get("opponent_territory_count", 0):
            s += 0.8 * d_opp
        else:
            s += 0.4 * d_opp
        return s

    best_s = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        sc = score_cell(nx, ny)
        if sc > best_s:
            best_s = sc
            best_move = [dx, dy]

    # If all moves blocked, stay.
    return best_move if best_move != [None, None] else [0, 0]