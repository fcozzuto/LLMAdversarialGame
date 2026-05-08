def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    blocks = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocks.add((x, y))

    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocks

    def manh(x, y, tx, ty):
        return abs(x - tx) + abs(y - ty)

    oxp, oyp = observation.get("opponent_position") or (w - 1, h - 1)
    oxp, oyp = int(oxp), int(oyp)

    opp_list = list(opp_terr)
    un_list = list(unclaimed)

    if opp_list:
        tx, ty = min(opp_list, key=lambda p: (manh(sx, sy, p[0], p[1]), p[0], p[1]))
        target_mode = 1  # contest
    elif un_list:
        tx, ty = min(un_list, key=lambda p: (manh(sx, sy, p[0], p[1]), p[0], p[1]))
        target_mode = 2  # expand
    else:
        tx, ty = oxp, oyp
        target_mode = 0

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = 0
        if (nx, ny) in opp_terr:
            v += 100000
        elif (nx, ny) in unclaimed:
            v += 5000
        elif (nx, ny) in self_terr:
            v += 50
        # deterministic pressure toward target
        dcur = manh(nx, ny, tx, ty)
        dnow = manh(sx, sy, tx, ty)
        v += (dnow - dcur) * (200 if target_mode == 1 else 120)
        # avoid drifting away from center slightly
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        v -= 0.1 * (abs(nx - cx) + abs(ny - cy))
        if (nx, ny) == (sx, sy) and target_mode != 0:
            v -= 5
        if v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]