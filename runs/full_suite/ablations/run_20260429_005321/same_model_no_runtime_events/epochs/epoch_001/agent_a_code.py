def choose_move(observation):
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((p[0], p[1]) for p in obstacles)
    cxands = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        # Move toward center while avoiding obstacles; also avoid opponent slightly
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        bestv = -10**18
        for dx, dy in cxands:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs_set:
                continue
            dist_center = max(abs(nx - tx), abs(ny - ty))
            dist_opp = max(abs(nx - ox), abs(ny - oy))
            v = -dist_center + 0.12 * dist_opp
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]
    # Choose move that maximizes advantage to a contested/uncontested resource
    best = (0, 0)
    bestv = -10**18
    cand_order = sorted(cxands, key=lambda t: (t[0], t[1]))
    for dx, dy in cand_order:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs_set:
            continue
        # If we can take a resource immediately, do so
        immediate = any((nx == rx and ny == ry) for rx, ry in resources)
        if immediate:
            # Prefer immediate with deterministic tie-break: nearest to opponent (to deny) and then lexicographic
            res = sorted([(rx, ry) for rx, ry in resources if rx == nx and ry == ny], key=lambda p: (p[0], p[1]))[0]
            v = 10**9 - 0.01 * max(abs(nx - ox), abs(ny - oy))
            best = (dx, dy)
            bestv = v
            break
        cur_best = 10**18
        for rx, ry in resources:
            myd = max(abs(nx - rx), abs(ny - ry))
            opd = max(abs(ox - rx), abs(oy - ry))
            # Lower is better: my distance adjusted by opponent contest
            score = myd - 0.35 * opd
            if score < cur_best or (score == cur_best and (rx, ry) < chosen_res):
                cur_best = score
                chosen_res = (rx, ry)
        # Encourage reducing our distance to the best resource vs current position
        rx, ry = chosen_res
        before = max(abs(sx - rx), abs(sy - ry))
        after = max(abs(nx - rx), abs(ny - ry))
        v = -cur_best + (before - after) * 0.6
        # Mild tie-break: closer to opponent denies space; deterministic by move ordering
        v += 0.02 * max(abs(nx - ox), abs(ny - oy)) * (-1)
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]