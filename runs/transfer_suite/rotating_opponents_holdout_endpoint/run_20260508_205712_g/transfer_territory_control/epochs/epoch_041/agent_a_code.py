def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    my_adj = set()
    for (x, y) in self_terr:
        for dx, dy in neigh8:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                my_adj.add((nx, ny))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        val = 0.0
        if (nx, ny) in opp_terr:
            val += 120.0
        elif (nx, ny) in unclaimed:
            val += 35.0
        elif (nx, ny) in self_terr:
            val += 5.0
        else:
            val += 10.0  # other claimed/invalid-ish cells

        if (nx, ny) in my_adj:
            val += 12.0

        # Prefer being farther from opponent to avoid being pressured; still allow captures via large bonus above.
        dist2o = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        val += min(30.0, dist2o / 2.0)

        # Gentle bias toward reducing distance to board center after conquest pressure.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist2c = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        val += -dist2c / 40.0

        if best is None or val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [0, 0] if best is None else [int(best[0]), int(best[1])]