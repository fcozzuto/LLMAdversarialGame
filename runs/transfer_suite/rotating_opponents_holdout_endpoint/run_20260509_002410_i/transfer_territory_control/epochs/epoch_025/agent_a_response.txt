def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    uc_set = set(unclaimed)
    if not unclaimed:
        targets = [c for c in opp_t] or [c for c in self_t] or [(sx, sy)]
    else:
        # Prefer cells near our territory (frontier), else globally nearest unclaimed
        near_self = []
        for (x, y) in unclaimed:
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                if (x+dx, y+dy) in self_t:
                    near_self.append((x, y))
                    break
        targets = near_self if near_self else unclaimed

    def min_dist_to_targets(x, y):
        best = 10**9
        # small deterministic pruning: check first 24 targets with smallest manhattan distance to current
        # to keep runtime low
        order = sorted(targets, key=lambda t: abs(t[0]-sx) + abs(t[1]-sy))
        for tx, ty in order[:24]:
            d = abs(tx-x) + abs(ty-y)
            if d < best:
                best = d
        return best if best < 10**9 else 0

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        in_self = (nx, ny) in self_t
        in_opp = (nx, ny) in opp_t
        in_uc = (nx, ny) in uc_set

        # Immediate value: claim unclaimed strongly; flip opponent moderately; keep self slightly
        immediate = (9 if in_uc else 0) + (5 if in_opp else 0) + (1 if in_self else 0)

        # Positional value: move toward good targets
        dist = min_dist_to_targets(nx, ny)
        # Encourage stepping closer; discourage wandering
        approach = -dist

        # Avoid getting immediately adjacent to opponent only if we can't gain much
        opp_dist = abs(nx-ox) + abs(ny-oy)
        safety = 0
        if immediate <= 1 and opp_dist <= 1:
            safety = -4

        score = immediate * 10 + approach * 2 + safety

        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # deterministic tie-break: prefer not moving diagonally, then toward positive x, then positive y
            if dx == best_move[0] and dy == best_move[1]:
                continue
            # diagonal penalty
            cur_diag = (dx != 0 and dy != 0)
            best_diag = (best_move[0] != 0 and best_move[1] != 0)
            if best_diag and not cur_diag:
                best_move = (dx, dy)
            elif cur_diag == best_diag:
                if dx > best_move[0] or (dx == best_move[0] and dy > best_move[1]):
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]