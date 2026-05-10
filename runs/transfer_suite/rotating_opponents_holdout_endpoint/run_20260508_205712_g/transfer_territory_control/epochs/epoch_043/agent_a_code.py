def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if ((int(observation.get("turn_index") or 0) & 1) == 0):
        neigh8 = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = (float("-inf"), 0, 0)
    for idx, (dx, dy) in enumerate(neigh8):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        if (nx, ny) in opp_terr:
            val = 3.0
        elif (nx, ny) in unclaimed:
            val = 1.6
        elif (nx, ny) in self_terr:
            val = 0.0
        else:
            val = 0.4

        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                    if (tx, ty) in opp_terr:
                        val += 0.25
                    elif (tx, ty) in self_terr:
                        val += 0.05

        dist_center = abs(nx - cx) + abs(ny - cy)
        val -= 0.01 * dist_center

        if (val > best[0]) or (val == best[0] and idx < best[1]):
            best = (val, idx, 0)
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]