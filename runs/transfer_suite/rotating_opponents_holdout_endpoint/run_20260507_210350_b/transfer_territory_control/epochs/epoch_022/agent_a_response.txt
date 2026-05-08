def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])

    def to_set(key):
        s = set()
        for p in observation.get(key, []) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    self_terr = to_set("self_territory")
    opp_terr = to_set("opponent_territory")

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in self_terr:
            score += 2
        if (nx, ny) in unclaimed:
            score += 14
        if (nx, ny) in opp_terr:
            score += 36

        dist_center = abs(nx - cx) + abs(ny - cy)
        score += int(20 - 2 * dist_center)

        # Prefer reducing distance to any "good" target deterministically
        if unclaimed:
            # pick nearest target with deterministic tie-break
            # (small scan: unclaimed count typically not huge)
            tx, ty = None, None
            best_d = None
            for (x, y) in unclaimed:
                d = abs(x - nx) + abs(y - ny)
                if best_d is None or d < best_d or (d == best_d and (y, x) < (ty, tx)):
                    best_d = d
                    tx, ty = x, y
            if tx is not None:
                score += max(0, 10 - best_d)
        else:
            # If nothing unclaimed, push toward opponent border via adjacency
            adj = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    if (nx + ax, ny + ay) in opp_terr:
                        adj += 1
            score += 5 * adj

        # Mild preference to move toward center on tie-break
        if (best is None) or (score > best_score):
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]