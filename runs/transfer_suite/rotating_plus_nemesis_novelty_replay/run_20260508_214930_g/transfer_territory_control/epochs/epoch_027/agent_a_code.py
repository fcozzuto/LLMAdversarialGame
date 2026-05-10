def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def neighbors_in_set(nx, ny, sset):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (nx + dx, ny + dy) in sset:
                    c += 1
        return c

    def best_cell_score(nx, ny):
        # Strongly favor entering opponent territory to counterclaim, otherwise grab unclaimed.
        base = 0
        if (nx, ny) in opp_t:
            base += 16
        elif (nx, ny) in unclaimed:
            base += 13
        elif (nx, ny) in self_t:
            base += 6
        else:
            base += 2  # should be unclaimed, but keep safe

        adj_opp = neighbors_in_set(nx, ny, opp_t)
        adj_self = neighbors_in_set(nx, ny, self_t)

        # Push toward opponent frontier while keeping some spread away from self clumping.
        base += 4 * adj_opp
        base -= 2 * adj_self

        # Slight preference toward center for long-term control.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist_center = abs(nx - cx) + abs(ny - cy)
        base -= 0.05 * dist_center

        return base

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        val = best_cell_score(nx, ny)
        # Deterministic tie-break: prefer staying if equal, else lexicographic on (dx,dy).
        if val > best_val or (val == best_val and ((dx, dy) < best_move) and (dx, dy) != (0, 0)):
            best_val = val
            best_move = (dx, dy)

    if not inside(sx + best_move[0], sy + best_move[1]):
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]