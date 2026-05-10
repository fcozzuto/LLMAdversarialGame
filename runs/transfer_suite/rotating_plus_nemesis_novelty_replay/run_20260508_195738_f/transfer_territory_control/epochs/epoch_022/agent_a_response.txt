def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obs_list = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obs_list)
    oppt_list = observation.get("opponent_territory", []) or []
    oppt = set((p[0], p[1]) for p in oppt_list)
    selft_list = observation.get("self_territory", []) or []
    selft = set((p[0], p[1]) for p in selft_list)
    unclaimed_list = observation.get("unclaimed_cells", []) or []
    unclaimed = set((p[0], p[1]) for p in unclaimed_list)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    opp_pos = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = opp_pos[0], opp_pos[1]

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

    # Prefer claiming border/edge cells, but keep distance from opponent territory.
    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_opp = min_dist_to_set(nx, ny, oppt)
        d_center = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)  # larger near edges
        d_from_opp_pos = abs(nx - ox) + abs(ny - oy)

        base = 0.0
        if (nx, ny) in selft:
            base += 0.4
        elif (nx, ny) in unclaimed:
            base += 2.2 + 0.15 * d_center
        elif (nx, ny) in oppt:
            base += 1.3  # flipping can be useful, but we heavily penalize getting too close overall
        else:
            base += 0.2  # unknown cells: neutral

        score = base
        score += 0.9 * d_opp
        score += 0.25 * d_from_opp_pos
        score -= 0.8 * (1 if (nx, ny) in oppt else 0) * (8 - d_center)  # avoid deep center flips

        # Tiny deterministic tiebreaker toward edges first, then dx/dy order
        score += 0.01 * d_center
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move