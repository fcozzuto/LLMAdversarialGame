def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    self_t = set((int(c[0]), int(c[1])) for c in (observation.get("self_territory") or []) if c and len(c) >= 2)
    opp_t = set((int(c[0]), int(c[1])) for c in (observation.get("opponent_territory") or []) if c and len(c) >= 2)
    unclaimed = set((int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c and len(c) >= 2)

    neigh8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    targets = []
    for x, y in unclaimed:
        if (x, y) not in self_t and (x, y) not in opp_t:
            for dx, dy in neigh8:
                nx, ny = x + dx, y + dy
                if (nx, ny) in opp_t:
                    targets.append((x, y))
                    break

    if not targets:
        for x, y in unclaimed:
            if (x, y) not in self_t and (x, y) not in opp_t:
                for dx, dy in neigh8:
                    nx, ny = x + dx, y + dy
                    if (nx, ny) in self_t:
                        targets.append((x, y))
                        break

    if not targets:
        return [0, 0]

    tx, ty = None, None
    bestd = 10**9
    for x, y in targets:
        d = abs(x - sx) + abs(y - sy)
        if d < bestd:
            bestd = d
            tx, ty = x, y

    moves = []
    for dx, dy in neigh8:
        nx, ny = sx + dx, sy + dy
        if dx == 0 and dy == 0:
            pass
        if not free(nx, ny):
            continue
        moves.append((dx, dy))

    def score_cell(x, y, dx, dy):
        sc = 0
        if (x, y) in unclaimed and (x, y) not in self_t and (x, y) not in opp_t:
            sc += 3
        if (x, y) in opp_t:
            sc += 6
        if (x, y) in self_t:
            sc += 1
        for ddx, ddy in neigh8:
            nx, ny = x + ddx, y + ddy
            if (nx, ny) in unclaimed and (nx, ny) not in self_t and (nx, ny) not in opp_t:
                sc += 1
            if (nx, ny) in opp_t:
                sc += 0.5
        sc += -0.08 * (abs(x - tx) + abs(y - ty))
        sc += -0.02 * (abs(x - ox) + abs(y - oy))
        return sc

    best = None
    bestsc = -1e18
    # deterministic tie-break: prefer smaller dx then dy
    for dx, dy in sorted(moves, key=lambda t: (t[0], t[1])):
        nx, ny = sx + dx, sy + dy
        sc = score_cell(nx, ny, dx, dy)
        if sc > bestsc:
            bestsc = sc
            best = [dx, dy]
    return best if best is not None else [0, 0]