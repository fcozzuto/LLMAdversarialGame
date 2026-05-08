def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for o in observation.get("obstacles") or []:
        try:
            x, y = o
        except Exception:
            continue
        obstacles.add((int(x), int(y)))

    opp_pos = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    self_cnt = int(observation.get("self_territory_count") or 0)
    opp_cnt = int(observation.get("opponent_territory_count") or 0)

    cx, cy = w // 2, h // 2
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (1, 1), (-1, 1), (1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cells_from_list(lst):
        out = []
        for p in lst or []:
            try:
                x, y = p
            except Exception:
                continue
            x, y = int(x), int(y)
            if inb(x, y):
                out.append((x, y))
        return out

    opp_terr = cells_from_list(observation.get("opponent_territory") or [])
    unclaimed = cells_from_list(observation.get("unclaimed_cells") or [])

    attack = self_cnt < opp_cnt
    if attack and opp_terr:
        tx, ty = min(opp_terr, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    else:
        if unclaimed:
            tx, ty = min(unclaimed, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
        else:
            tx, ty = cx, cy

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dtx = abs(nx - tx) + abs(ny - ty)
        dto = abs(nx - ox) + abs(ny - oy)
        score = (-dtx) + (0.05 * dto)
        if score > best_score:
            best_score = score
            best = [dx, dy]
    return best if best is not None else [0, 0]