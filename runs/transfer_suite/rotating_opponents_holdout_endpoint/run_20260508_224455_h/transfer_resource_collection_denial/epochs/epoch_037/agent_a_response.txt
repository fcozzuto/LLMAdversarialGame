def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))

    if not resources or not valid:
        return [0, 0]

    res_set = set((p[0], p[1]) for p in resources)

    def man(x1, y1, x2, y2):
        d1 = x1 - x2
        if d1 < 0: d1 = -d1
        d2 = y1 - y2
        if d2 < 0: d2 = -d2
        return d1 + d2

    # Two-level deterministic policy:
    # 1) If a move collects immediately, take the one that maximizes denier margin for remaining.
    # 2) Else, move to improve the best denier margin attainable from next cell.
    best = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy

        immediate = 1 if (nx, ny) in res_set else 0
        if immediate:
            # After immediate, approximate by considering the best future denier target from nx,ny.
            best_margin = -10**9
            best_selfdist = 10**9
            for rx, ry in resources:
                if rx == nx and ry == ny:
                    continue
                sd = man(nx, ny, rx, ry)
                od = man(ox, oy, rx, ry)
                margin = od - sd
                if margin > best_margin or (margin == best_margin and sd < best_selfdist):
                    best_margin = margin
                    best_selfdist = sd
            val = 10**7 + best_margin * 100 - best_selfdist
        else:
            # Choose move that makes the best reachable resource deniable from next cell.
            best_margin = -10**9
            best_selfdist = 10**9
            best_oppdist = 10**9
            for rx, ry in resources:
                sd = man(nx, ny, rx, ry)
                od = man(ox, oy, rx, ry)
                margin = od - sd
                # Tie-break: prefer larger margin; then smaller self distance; then smaller opp distance.
                if (margin > best_margin or
                    (margin == best_margin and sd < best_selfdist) or
                    (margin == best_margin and sd == best_selfdist and od < best_oppdist)):
                    best_margin = margin
                    best_selfdist = sd
                    best_oppdist = od
            # Encourage progress even if margin is negative; small step-cost discourages staying.
            val = best_margin * 100 - best_selfdist - (1 if dx == 0 and dy == 0 else 0)

        if best is None or val > best[0] or (val == best[0] and (dx, dy) < best[1]):
            best = (val, (dx, dy))

    return [best[1][0], best[1][1]]