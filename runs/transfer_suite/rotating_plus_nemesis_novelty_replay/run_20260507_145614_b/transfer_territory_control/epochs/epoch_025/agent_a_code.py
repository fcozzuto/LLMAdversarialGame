def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            unclaimed.add((p[0], p[1]))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            resources.append((p[0], p[1]))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = [0, 0]
    bestv = -10**30
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        v = 0.0
        if (nx, ny) in unclaimed:
            v += 50.0

        v += -0.01 * ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))

        if resources:
            md2 = None
            for rx, ry in resources:
                d2 = (nx - rx) * (nx - rx) + (ny - ry) * (ny - ry)
                if md2 is None or d2 < md2:
                    md2 = d2
            v += 100.0 / (1.0 + md2)

        d2o = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        v += 5.0 / (1.0 + d2o)

        # Deterministic tie-break: keep earlier best; also penalize non-moves slightly
        if v > bestv + 1e-12 or (abs(v - bestv) <= 1e-12 and (dx != 0 or dy != 0) and (best == [0, 0])):
            bestv = v
            best = [dx, dy]

    return best