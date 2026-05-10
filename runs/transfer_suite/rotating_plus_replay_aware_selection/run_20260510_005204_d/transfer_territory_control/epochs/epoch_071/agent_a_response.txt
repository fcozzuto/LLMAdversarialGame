def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set(tuple(p) for p in observation.get("self_territory") or [] if p and len(p) >= 2)
    oppT = set(tuple(p) for p in observation.get("opponent_territory") or [] if p and len(p) >= 2)
    unclaimed = set(tuple(p) for p in observation.get("unclaimed_cells") or [] if p and len(p) >= 2)
    resources = set(tuple(p) for p in observation.get("resources") or [] if p and len(p) >= 2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    unclaimed_or_opp = [c for c in unclaimed] if unclaimed else [c for c in (unclaimed | oppT)]
    targets = list(unclaimed_or_opp) if unclaimed_or_opp else [(0, 0)]

    def dist_to_targets(nx, ny):
        best = 10**9
        for tx, ty in targets:
            d = abs(nx - tx) + abs(ny - ty)
            if d < best:
                best = d
        return best

    def score_cell(nx, ny):
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            return -10**9
        s = 0
        on_border = 1 if (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1) else 0
        s += 3 * on_border

        if (nx, ny) in oppT:
            s += 12
        elif (nx, ny) in unclaimed:
            s += 6
        elif (nx, ny) in selfT:
            s += 1

        d_t = dist_to_targets(nx, ny)
        s += -0.4 * d_t

        d_opp = abs(nx - ox) + abs(ny - oy)
        s += 0.08 * (7 - d_opp)

        if resources:
            d_r = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
            s += -0.2 * d_r
        return s

    best = None
    best_s = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        sc = score_cell(nx, ny)
        if sc > best_s:
            best_s = sc
            best = (dx, dy)
    return [int(best[0]), int(best[1])] if best is not None else [0, 0]