def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    center = ((w - 1) / 2.0, (h - 1) / 2.0)

    best = (float("-inf"), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in opp_terr:
            score = 10.0
        elif (nx, ny) in unclaimed:
            score = 4.2
        elif (nx, ny) in self_terr:
            score = 1.2
        else:
            score = 1.0

        if (nx, ny) in resources:
            score += 3.5

        d_opp = abs(nx - ox) + abs(ny - oy)
        if (nx, ny) in opp_terr:
            score += 0.3 * d_opp  # keep extending from contact
        else:
            score -= 0.25 * max(0, 4 - d_opp)  # avoid getting trapped near opponent

        # Encourage moving toward the nearest "frontier" (unclaimed adjacent to opp terr).
        # Compute cheap frontier target direction by checking 8-neighborhood membership.
        frontier = False
        for tx, ty in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            ax, ay = nx + tx, ny + ty
            if (ax, ay) in unclaimed:
                # if unclaimed would be adjacent to opponent territory, treat as frontier
                for ex, ey in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                    bx, by = ax + ex, ay + ey
                    if (bx, by) in opp_terr:
                        frontier = True
                        break
                if frontier:
                    break
        if frontier:
            score += 2.0

        cx, cy = center
        score += -0.01 * (abs(nx - cx) + abs(ny - cy))  # slight centrality

        if score > best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]