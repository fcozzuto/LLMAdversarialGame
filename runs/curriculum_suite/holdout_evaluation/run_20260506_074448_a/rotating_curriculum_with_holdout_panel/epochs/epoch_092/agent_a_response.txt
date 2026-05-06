def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = [(r[0], r[1]) for r in (observation.get("resources") or []) if 0 <= r[0] < w and 0 <= r[1] < h and (r[0], r[1]) not in obstacles]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def steps(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy  # Chebyshev distance

    def best_target():
        if not resources:
            return None
        alpha = 1.35  # prefer denying opponent closer resources
        best = None
        for rx, ry in resources:
            ms = steps(sx, sy, rx, ry)
            os = steps(ox, oy, rx, ry)
            # also bias toward resources that are on/near my row or column (helps vs row-sweep)
            axis = (rx == sx) or (ry == sy) or (abs(rx - sx) <= 1) or (abs(ry - sy) <= 1)
            axis_bonus = -0.4 if axis else 0.0
            v = (ms - alpha * os) + axis_bonus + 0.01 * (rx * 0 + ry * 0 + ms)  # deterministic tie-break-ish
            if best is None or v < best[0]:
                best = (v, rx, ry)
        return best[1], best[2] if best else None

    target = best_target()

    def center_towards():
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        tx = 0 if sx == cx else (1 if sx < cx else -1)
        ty = 0 if sy == cy else (1 if sy < cy else -1)
        return tx, ty

    if target is None:
        tx, ty = center_towards()
        best_move = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                # pick move that aligns with center direction deterministically
                align = -((dx - tx) * (dx - tx) + (dy - ty) * (dy - ty))
                if best_move is None or align > best_move[0]:
                    best_move = (align, dx, dy)
        return [best_move[1], best_move[2]] if best_move else [0, 0]

    rx, ry = target
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            my_after = steps(nx, ny, rx, ry)
            opp_to = steps(ox, oy, rx, ry)
            # if multiple options, pick the one that makes me closer to my target
            # and also keeps me from stepping into a cell that would let opp be strictly closer to many resources
            deny = 0
            for ax, ay in resources:
                if steps(ox, oy, ax, ay) + 0 <= steps(nx, ny, ax, ay) - 1:
                    deny += 1
            v = (my_after - 1.25 * opp_to) - 0.05 * deny
            # deterministic tie-break: prefer smaller dx, then smaller dy
            v2 = (v, abs(dx), abs(dy), dx, dy)
            if best is None or v2 < best[0]:
                best = (v2, dx, dy)
    return [best[1], best[2]] if best else [0, 0]