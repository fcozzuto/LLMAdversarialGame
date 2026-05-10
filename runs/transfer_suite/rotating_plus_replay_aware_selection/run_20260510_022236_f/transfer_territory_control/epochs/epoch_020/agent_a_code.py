def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    self_set = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_set = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = observation.get("unclaimed_cells") or []

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_target = None
    if unclaimed:
        cand = []
        for p in unclaimed:
            if not (isinstance(p, (list, tuple)) and len(p) >= 2):
                continue
            tx, ty = int(p[0]), int(p[1])
            if not (0 <= tx < w and 0 <= ty < h):
                continue
            if (tx, ty) in blocked:
                continue
            dc = abs(tx - cx) + abs(ty - cy)
            do = abs(tx - ox) + abs(ty - oy)
            cand.append((dc, -do, abs(tx - sx) + abs(ty - sy), tx, ty))
        if cand:
            cand.sort()
            best_target = (cand[0][3], cand[0][4])

    if best_target is None:
        best_target = (ox, oy)

    target_x, target_y = int(best_target[0]), int(best_target[1])

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        md = abs(target_x - nx) + abs(target_y - ny)
        val = -md

        if (nx, ny) in self_set:
            val += 0.05
        elif (nx, ny) in opp_set:
            val += 0.85
        elif (nx, ny) in (set(tuple(p) for p in unclaimed) if unclaimed else set()):
            val += 0.35

        if max(abs(nx - ox), abs(ny - oy)) <= 1:
            val -= 0.25

        if abs(nx - cx) + abs(ny - cy) < abs(sx - cx) + abs(sy - cy):
            val += 0.08

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]