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

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0

    up = int(observation.get("self_territory_count") or 0)
    op = int(observation.get("opponent_territory_count") or 0)
    we_lead = up >= op

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    opp_list = list(op_terr)
    un_list = list(unclaimed)

    def mindist(x, y, cells, fallback=10**9):
        if not cells:
            return fallback
        best = fallback
        cap = 80 if len(cells) > 80 else len(cells)
        for i in range(cap):
            cx, cy = cells[i]
            d = abs(cx - x) + abs(cy - y)
            if d < best:
                best = d
                if best == 0:
                    break
        return best

    target_cells = un_list if (not we_lead or not un_list) else opp_list
    next_valid_found = False
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        next_valid_found = True

        in_self = (nx, ny) in self_terr
        in_un = (nx, ny) in unclaimed
        in_op = (nx, ny) in op_terr

        dist_center = abs(nx - cx0) + abs(ny - cy0)
        dist_target = mindist(nx, ny, target_cells)

        # Prefer expanding/stealing; being near center helps vs center-claimers.
        val = 0.0
        val += -0.9 * dist_center
        if in_un:
            val += 40.0
        if in_op:
            val += 30.0 if not we_lead else 22.0
        if in_self:
            val += 6.0
        # Move toward the chosen target set.
        val += -2.2 * dist_target

        # Small tie-breaker: prefer moves that reduce distance to any opponent territory.
        if opp_list:
            val += -0.3 * mindist(nx, ny, opp_list)

        # Deterministic tie-break: lexicographic by (dx, dy)
        if (val > best_val) or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    if not next_valid_found:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]