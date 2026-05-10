def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    x, y = int(sp[0]), int(sp[1])

    self_t = observation.get("self_territory") or []
    opp_t = observation.get("opponent_territory") or []
    obs_list = observation.get("obstacles") or []
    unclaimed = observation.get("unclaimed_cells") or []

    self_set = set((int(p[0]), int(p[1])) for p in self_t if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_set = set((int(p[0]), int(p[1])) for p in opp_t if isinstance(p, (list, tuple)) and len(p) >= 2)
    blocked = set((int(p[0]), int(p[1])) for p in obs_list if isinstance(p, (list, tuple)) and len(p) >= 2)
    targets = [(int(p[0]), int(p[1])) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2]

    opp_pos = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(a, b):
        return 0 <= a < w and 0 <= b < h

    def min_manh(px, py, pts):
        best = 10**9
        for tx, ty in pts:
            d = abs(tx - px) + abs(ty - py)
            if d < best:
                best = d
        return best

    # Priorities: when behind, expand to unclaimed; when ahead, press toward opponent.
    self_count = int(observation.get("self_territory_count") or len(self_set))
    opp_count = int(observation.get("opponent_territory_count") or len(opp_set))
    behind = self_count < opp_count

    # Frontier preference: cells near either opponent territory or unclaimed.
    focus_unclaimed = targets if targets else list(opp_set) if opp_set else []
    d_unclaimed_from_opp = min_manh(ox, oy, focus_unclaimed) if focus_unclaimed else 10**9

    best_val = -10**18
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in blocked:
            continue

        val = 0
        if (nx, ny) in self_set:
            val += 2
        elif (nx, ny) in unclaimed:
            val += 7
        elif (nx, ny) in opp_set:
            val += 5
        else:
            val += 1

        # Distance heuristics (deterministic tie-break by move order via iteration).
        if targets:
            d1 = min_manh(nx, ny, targets)
            val += (-2.2 * d1)  # closer to unclaimed is better
        val += (-1.2 * (abs(nx - ox) + abs(ny - oy)))  # also move toward opponent

        # If unclaimed exists near opponent, slightly favor paths toward that region when ahead.
        if not behind and focus_unclaimed:
            val += (-0.4 * abs(min_manh(nx, ny, focus_unclaimed) - d_unclaimed_from_opp))

        # Mild preference for expanding into cells adjacent to unclaimed.
        if targets:
            adj_unclaimed = 0
            for adx in (-1, 0, 1):
                for ady in (-1, 0, 1):
                    if adx == 0 and ady == 0:
                        continue
                    axx, ayy = nx + adx, ny + ady
                    if in_bounds(axx, ayy) and (axx, ayy) in set(targets):
                        adj_unclaimed += 1
            val += 0.6 * adj_unclaimed

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]