def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_t = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    opp_front = set()
    for (x, y) in opp_t:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in unclaimed:
                    opp_front.add((nx, ny))

    targets = []
    res = observation.get("resources") or []
    for p in res:
        if p and len(p) >= 2:
            t = (int(p[0]), int(p[1]))
            if inb(t[0], t[1]):
                targets.append(t)
    if not targets:
        if opp_front:
            targets = list(opp_front)
        else:
            targets = list(unclaimed) if unclaimed else []

    def score_cell(x, y):
        if not inb(x, y):
            return -10**9
        s = 0
        if (x, y) in unclaimed:
            s += 6
        if (x, y) in opp_t:
            s += 10  # likely flips on entry
        if (x, y) in self_t:
            s += 2
        # bias toward nearest target
        if targets:
            md = min(abs(x - tx) + abs(y - ty) for (tx, ty) in targets)
            s += max(0, 6 - md)
        # slight center pressure
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        s += int(2 - (abs(x - cx) + abs(y - cy)) * 0.3)
        return s

    best = None
    best_sc = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                nx, ny = sx, sy
            else:
                nx, ny = sx + dx, sy + dy
            sc = score_cell(nx, ny)
            if sc > best_sc:
                best_sc = sc
                best = (dx, dy)

    return [int(best[0]), int(best[1])] if best is not None else [0, 0]