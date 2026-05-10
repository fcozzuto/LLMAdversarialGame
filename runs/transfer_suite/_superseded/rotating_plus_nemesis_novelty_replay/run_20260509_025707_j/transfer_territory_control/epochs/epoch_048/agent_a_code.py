def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(x, y) for (x, y) in (observation.get("obstacles") or [])}
    my = {(x, y) for (x, y) in (observation.get("self_territory") or [])}
    opp = {(x, y) for (x, y) in (observation.get("opponent_territory") or [])}
    un = {(x, y) for (x, y) in (observation.get("unclaimed_cells") or [])}

    myc = observation.get("self_territory_count", len(my))
    opc = observation.get("opponent_territory_count", len(opp))
    behind = myc < opc

    def adj_opp(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in opp:
                        c += 1
        return c

    def clamp_in(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    target_list = list(un) if un else list(opp)
    best = None
    best_sc = -10**9

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not clamp_in(nx, ny):
                nx, ny = sx, sy
                if (nx, ny) in obstacles:
                    nx, ny = sx, sy
            if (nx, ny) == (sx, sy):
                pass
            gain = 0
            if (nx, ny) in un:
                gain += 3
            elif (nx, ny) in opp:
                gain += 6 if behind else 4
            elif (nx, ny) in my:
                gain += 0
            else:
                gain += 1  # should be unclaimed, but be safe

            risk = adj_opp(nx, ny)
            # When ahead, avoid walking into their counterclaim zone
            avoid = (2 if not behind else 1) * risk
            # Nudge toward objectives: unclaimed if behind/even, else attack their nearest
            if target_list:
                tx, ty = min(target_list, key=lambda p: manh(nx, ny, p[0], p[1]))
                dist_term = -0.15 * manh(nx, ny, tx, ty)
            else:
                dist_term = 0
            # Prefer moves that advance toward opponent side (diagonal pressure)
            adv = 0.05 * (nx - sx) * (1 if sy <= h//2 else -1) + 0.05 * (ny - sy) * (1 if sx <= w//2 else -1)
            sc = gain + dist_term + adv - avoid

            if sc > best_sc or (sc == best_sc and (nx, ny) < (best[0], best[1]) if best else True):
                best_sc = sc
                best = (nx, ny)

    return [best[0] - sx, best[1] - sy]