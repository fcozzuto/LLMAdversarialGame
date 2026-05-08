def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    self_terr = set()
    for p in observation.get("self_territory") or []:
        try:
            self_terr.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        try:
            opp_terr.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        try:
            unclaimed.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cur_d = abs(sx - ox) + abs(sy - oy)
    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in opp_terr:
            base = -10**8
        elif (nx, ny) in unclaimed:
            base = 12
        elif (nx, ny) in self_terr:
            base = 6
        else:
            base = 3
        d_new = abs(nx - ox) + abs(ny - oy)
        center = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
        val = base + (d_new - cur_d) * 0.7 - center * 0.01
        if val > best[0]:
            best = (val, dx, dy)
    return [best[1], best[2]]