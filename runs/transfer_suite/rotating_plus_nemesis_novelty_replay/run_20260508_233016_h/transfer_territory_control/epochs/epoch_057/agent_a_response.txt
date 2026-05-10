def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    self_cells = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_cells = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs = [(dx, dy) for dx, dy in candidates]

    def best_dist_to_set(nx, ny, S, cap=64):
        dmin = 10**9
        for tx, ty in S:
            d = abs(nx - tx) + abs(ny - ty)
            if d < dmin:
                dmin = d
                if dmin == 0:
                    return 0
        return dmin

    opp_near = None
    if opp_cells:
        opp_near = best_dist_to_set(sx, sy, opp_cells)

    best = [0, 0]
    best_score = -10**18

    # Prioritize flipping opponent territory if reachable this step; otherwise expand toward border/unclaimed.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        is_opp = (nx, ny) in opp_cells
        is_uncl = (nx, ny) in unclaimed

        # Encourage stepping onto opponent-owned cells (flip on entry).
        if is_opp:
            score = 10**12 - (abs(nx - ox) + abs(ny - oy))
        else:
            # Move toward nearest opponent territory to pressure their claim.
            d_opp = best_dist_to_set(nx, ny, opp_cells) if opp_cells else 10**9
            # Move toward unclaimed cells to secure territory if we're not close to them.
            d_uncl = best_dist_to_set(nx, ny, unclaimed) if unclaimed else 10**9

            # Also prefer staying adjacent to our own territory to avoid accidental drift.
            adj_self = 0
            for ax, ay in dirs:
                px, py = nx + ax, ny + ay
                if (px, py) in self_cells:
                    adj_self += 1

            # Blend: if we are relatively close to opponent, bias toward them.
            closeness = 1.0 / (1 + d_opp)
            score = (
                5000 * adj_self
                + (3000 * closeness - 2000) * d_opp
                + 800 * (1 - closeness) * d_uncl
                - 3 * (abs(nx - ox) + abs(ny - oy))
            )

            # Slightly prefer moves that reduce distance to nearest unclaimed border-ish areas.
            if unclaimed:
                score += -20 * (nx + ny) % 3

        if score > best_score or (score == best_score and [dx, dy] < best):
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]