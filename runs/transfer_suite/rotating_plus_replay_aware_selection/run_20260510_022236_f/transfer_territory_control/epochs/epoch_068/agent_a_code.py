def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    up = int(observation.get("self_territory_count") or 0)
    op = int(observation.get("opponent_territory_count") or 0)
    chasing = up < op

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def has_adj_territ(cell, terr):
        cx, cy = cell
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (cx + dx, cy + dy) in terr:
                        return True
        return False

    target = None
    best = 10**9
    if unclaimed:
        for c in unclaimed:
            if chasing:
                if not has_adj_territ(c, op_terr):
                    continue
                tx, ty = c
                d = (tx - sx) * (tx - sx) + (ty - sy) * (ty - sy)
                if d < best:
                    best = d
                    target = c
            else:
                if not has_adj_territ(c, self_terr):
                    continue
                tx, ty = c
                d = (tx - sx) * (tx - sx) + (ty - sy) * (ty - sy)
                if d < best:
                    best = d
                    target = c

    if target is None:
        tx, ty = (ox, oy) if chasing else (sx, sy)
    else:
        tx, ty = target

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if target is None and chasing:
            dist = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            score = -dist
        else:
            dist = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
            score = -dist

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]