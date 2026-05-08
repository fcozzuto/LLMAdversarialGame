def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    self_t = set()
    for c in observation.get("self_territory") or []:
        if c and len(c) >= 2:
            self_t.add((int(c[0]), int(c[1])))
    opp_t = set()
    for c in observation.get("opponent_territory") or []:
        if c and len(c) >= 2:
            opp_t.add((int(c[0]), int(c[1])))

    unclaimed = []
    for c in observation.get("unclaimed_cells") or []:
        if c and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if free(x, y):
                if (x, y) not in self_t and (x, y) not in opp_t:
                    unclaimed.append((x, y))

    neigh8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    def adj_to_set(x, y, s):
        for dx, dy in neigh8:
            if (x + dx, y + dy) in s:
                return True
        return False

    best = None
    best_key = None
    for x, y in unclaimed:
        d = max(abs(x - sx), abs(y - sy))
        our_adj = adj_to_set(x, y, self_t)
        opp_adj = adj_to_set(x, y, opp_t)
        # Priority: move to cells adjacent to opponent territory to enable flipping pressure.
        key = (0 if opp_adj else 1, 0 if our_adj else 1, d, (x, y))
        if best is None or key < best_key:
            best, best_key = (x, y), key

    if best is None:
        # Fallback: head toward opponent (attempt to enter/contest) with obstacle avoidance.
        tx, ty = ox, oy
    else:
        tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    curd = max(abs(sx - tx), abs(sy - ty))
    best_move = (0, 0)
    best_md = curd + 10
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        md = max(abs(nx - tx), abs(ny - ty))
        # Prefer strict improvement; then deterministic tie-breaker via move order.
        if md < best_md:
            best_md = md
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]