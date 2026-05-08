def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    pos = observation.get("self_position") or (0, 0)
    ox = observation.get("opponent_position") or pos
    sx, sy = int(pos[0]), int(pos[1])
    px, py = int(ox[0]), int(ox[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def score_cell(x, y):
        if (x, y) in self_terr:
            s = -2
        else:
            s = 0
        if (x, y) in opp_terr:
            s -= 10
        if (x, y) in unclaimed:
            s += 25
        bx = x == 0 or x == w - 1
        by = y == 0 or y == h - 1
        s += 2 if (bx or by) else 0
        s -= (abs(x - px) + abs(y - py)) * 0.5
        s += 3 if (x, y) in unclaimed else 0
        return s

    def best_target():
        cand = []
        if opp_terr and unclaimed:
            for tx, ty in unclaimed:
                if (abs(tx - px) <= 2 and abs(ty - py) <= 2) and (tx, ty) not in obstacles:
                    cand.append((tx, ty))
        if cand:
            cand.sort(key=lambda c: (-(score_cell(c[0], c[1])) , abs(c[0] - px) + abs(c[1] - py)))
            return cand[0]
        if unclaimed:
            tlist = [t for t in unclaimed if t not in obstacles]
            if tlist:
                tlist.sort(key=lambda t: (-(score_cell(t[0], t[1])) , abs(t[0] - sx) + abs(t[1] - sy)))
                return tlist[0]
        return (w // 2, h // 2)

    tx, ty = best_target()

    best = (0, 0)
    best_s = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        s = -((nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)) + score_cell(nx, ny)
        if best_s is None or s > best_s or (s == best_s and (dx, dy) < best):
            best_s = s
            best = (dx, dy)

    return [int(best[0]), int(best[1])]