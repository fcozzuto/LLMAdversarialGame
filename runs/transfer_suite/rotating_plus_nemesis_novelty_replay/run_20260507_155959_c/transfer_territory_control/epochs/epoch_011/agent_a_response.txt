def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = (observation.get("self_position", [0, 0]) + [0, 0])[:2]
    ox, oy = (observation.get("opponent_position", [w - 1, h - 1]) + [w - 1, h - 1])[:2]
    obstacles = set(tuple(p[:2]) for p in (observation.get("obstacles") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    self_cells = set(tuple(p[:2]) for p in (observation.get("self_territory") or []) if len(p) >= 2)
    opp_cells = set(tuple(p[:2]) for p in (observation.get("opponent_territory") or []) if len(p) >= 2)
    unclaimed = [tuple(p[:2]) for p in (observation.get("unclaimed_cells") or []) if len(p) >= 2]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Deterministic target: nearest unclaimed that is not blocked; if none, chase opponent or center.
    if unclaimed:
        best = None
        for x, y in unclaimed:
            if (x, y) in obstacles or not inb(x, y):
                continue
            d = abs(x - sx) + abs(y - sy)
            # Prefer cells closer to opponent side to reduce their expansion.
            tieb = abs(x - ox) + abs(y - oy)
            score = (d, -tieb, x, y)
            if best is None or score < best[0]:
                best = (score, (x, y))
        target = best[1] if best else (ox, oy)
    else:
        # If no unclaimed: attack nearest opponent cell; else move toward board center.
        if opp_cells:
            best = None
            for x, y in opp_cells:
                if (x, y) in obstacles or not inb(x, y):
                    continue
                d = abs(x - sx) + abs(y - sy)
                score = (d, x, y)
                if best is None or score < best[0]:
                    best = (score, (x, y))
            target = best[1] if best else (ox, oy)
        else:
            target = (w // 2, h // 2)

    # Pick best move by local capture/flip potential and distance to target; avoid obstacles.
    tx, ty = target
    best_move = [0, 0]
    best_val = None
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Heuristic components
        cell_in_self = (nx, ny) in self_cells
        cell_in_opp = (nx, ny) in opp_cells
        cell_unclaimed = (nx, ny) not in self_cells and (nx, ny) not in opp_cells
        dist_t = abs(nx - tx) + abs(ny - ty)
        dist_o = abs(nx - ox) + abs(ny - oy)
        # Prefer immediate territory gain; slight preference toward opponent side.
        val = 0
        if cell_unclaimed:
            val += 50
        if cell_in_opp:
            val += 120
        if cell_in_self:
            val += 5
        val += (200 - dist_t) * 0.2
        val += dist_o * -0.05
        # Deterministic tie-breaker
        tie = (val, cell_in_opp, cell_unclaimed, -dist_t, nx, ny)
        if best_val is None or tie > best_val:
            best_val = tie
            best_move = [dx, dy]

    # If all moves blocked (shouldn't), stay put.
    return best_move if isinstance(best_move, list) else [0, 0]