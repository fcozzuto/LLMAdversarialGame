def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    self_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    unclaimed = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}
    ox, oy = observation["opponent_position"]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def adj_to_opp(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in opp_set:
                    return True
        return False

    def score_cell(nx, ny):
        # Strongly prefer flipping an opponent cell
        if (nx, ny) in opp_set:
            return 1000 - (abs(nx - ox) + abs(ny - oy))
        # Prefer claiming unclaimed, especially near opponent front
        if (nx, ny) in unclaimed:
            s = 80 - (abs(nx - ox) + abs(ny - oy)) * 0.2
            if adj_to_opp(nx, ny):
                s += 40
            return s
        # If moving into our own territory, keep advancing toward the opponent
        if (nx, ny) in self_set:
            # Encourage closing distance while avoiding dead-ends behind our front
            return 20 - (abs(nx - ox) + abs(ny - oy)) * 0.5
        # Unknown cell (shouldn't happen often), treat as low
        return -5

    myc = observation.get("self_territory_count", len(self_set))
    opc = observation.get("opponent_territory_count", len(opp_set))
    behind = myc < opc

    # If behind, prioritize immediate capture; if ahead, prefer frontier expansion toward opponent
    best = (-(10**18), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        base = score_cell(nx, ny)
        # Mild bias to keep moving toward opponent even if not flipping this step
        dist = abs(nx - ox) + abs(ny - oy)
        if behind and (nx, ny) in opp_set:
            base += 500
        if (nx, ny) in unclaimed and adj_to_opp(nx, ny):
            base += 60 if behind else 30
        base += -dist * (2.5 if behind else 1.5)
        # Deterministic tie-break: prefer fewer coordinate changes (stay) then lexicographic
        tie = (0 if (dx == 0 and dy == 0) else 1, dx, dy)
        if base > best[0] or (base == best[0] and tie < (best[1], best[2], best[2])):
            best = (base, dx, dy)

    return [int(best[1]), int(best[2])]