def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                self_terr.add((x, y))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_terr.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))

    ox, oy = observation.get("opponent_position") or (sx, sy)
    ox, oy = int(ox), int(oy)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = [[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
    best = None
    bestv = -1e18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            v = -1e12
        elif (nx, ny) in obstacles:
            v = -1e12
        else:
            v = 0.0
            if (nx, ny) in opp_terr:
                v += 2.5
            elif (nx, ny) in unclaimed:
                v += 1.8
            elif (nx, ny) in self_terr:
                v += 0.4

            # Prefer interior expansion and cutting off opponent
            v += -0.12 * (abs(nx - cx) + abs(ny - cy))
            v += -0.01 * (abs(nx - ox) + abs(ny - oy))

            # Slight preference for moving away from obstacles' immediate neighborhood
            # (helps avoid getting stuck at borders/near blockers deterministically)
            near_obs = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    if (nx + ax, ny + ay) in obstacles:
                        near_obs += 1
            v += -0.15 * near_obs

        if v > bestv:
            bestv = v
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]