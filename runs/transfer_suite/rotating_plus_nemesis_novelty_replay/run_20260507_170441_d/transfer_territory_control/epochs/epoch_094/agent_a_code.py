def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best = None
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue

        cell_type = 0
        if (nx, ny) in opp_t:
            cell_type = 3
        elif (nx, ny) in unclaimed:
            cell_type = 2
        elif (nx, ny) in self_t:
            cell_type = 1

        d_opp = abs(nx - ox) + abs(ny - oy)
        d_self = abs(nx - sx) + abs(ny - sy)

        # Prefer advancing toward opponent while expanding into new cells.
        score = 0
        score += cell_type * 1000
        score += (30 - d_opp) * (10 if cell_type >= 2 else 2)
        score -= d_self  # discourage large moves when not needed

        # If we're near opponent territory, prioritize cutting into it.
        if opp_t:
            adj_opp = False
            for adx, ady in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
                if (nx + adx, ny + ady) in opp_t:
                    adj_opp = True
                    break
            if adj_opp:
                score += 220 if cell_type >= 2 else 80

        # Deterministic tie-break: prefer diagonal, then right, then down (stable ordering via score + dir weight).
        dir_weight = (dx + 1) * 3 + (dy + 1)
        score += (dir_weight % 7) * 0.001

        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]