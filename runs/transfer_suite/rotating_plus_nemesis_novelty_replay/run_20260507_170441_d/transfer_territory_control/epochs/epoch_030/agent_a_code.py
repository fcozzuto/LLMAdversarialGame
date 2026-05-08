def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        sx, sy, ox, oy = 0, 0, 0, 0

    blocked = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
        except:
            continue
        if 0 <= x < w and 0 <= y < h:
            blocked.add((x, y))

    self_t = set()
    for p in observation.get("self_territory") or []:
        try:
            self_t.add((int(p[0]), int(p[1])))
        except:
            pass

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def score_cell(nx, ny):
        d_opp = abs(nx - ox) + abs(ny - oy)
        if (nx, ny) in self_t:
            own_bonus = -2
        else:
            own_bonus = 0
        unclaimed = observation.get("unclaimed_cells") or []
        un = set()
        if unclaimed:
            for p in unclaimed:
                try:
                    un.add((int(p[0]), int(p[1])))
                except:
                    pass
        un_bonus = -1 if (nx, ny) in un else 0
        return d_opp + own_bonus + un_bonus

    best = None
    best_s = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        s = score_cell(nx, ny)
        if best_s is None or s < best_s:
            best_s = s
            best = [dx, dy]

    if best is not None:
        return best
    return [0, 0]