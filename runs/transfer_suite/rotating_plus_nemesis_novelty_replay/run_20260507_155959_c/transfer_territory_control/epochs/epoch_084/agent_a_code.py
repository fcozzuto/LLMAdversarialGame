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

    self_t = set((int(c[0]), int(c[1])) for c in (observation.get("self_territory") or []) if c and len(c) >= 2)
    opp_t = set((int(c[0]), int(c[1])) for c in (observation.get("opponent_territory") or []) if c and len(c) >= 2)
    unclaimed = [(int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c and len(c) >= 2]

    neigh8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    def adj_to_set(x, y, s):
        for dx, dy in neigh8:
            if (x + dx, y + dy) in s:
                return True
        return False

    targets = []
    for x, y in unclaimed:
        if free(x, y) and (x, y) not in self_t and (x, y) not in opp_t:
            adj_opp = adj_to_set(x, y, opp_t) if opp_t else False
            d_self = abs(x - sx) + abs(y - sy)
            d_opp = abs(x - ox) + abs(y - oy)
            score = (10 if adj_opp else 0) - d_self * 0.35 + d_opp * 0.02
            targets.append((score, d_self, x, y, adj_opp))
    if not targets:
        return [0, 0]

    targets.sort(reverse=True)
    _, _, tx, ty, _ = targets[0]

    moves = [(0, 0)]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            moves.append((dx, dy))

    def step_score(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            return -10**9
        # Prefer actions that move closer to target; slight bias toward staying near self territory edge
        d_now = abs(nx - tx) + abs(ny - ty)
        d_tgt = abs(sx - tx) + abs(sy - ty)
        near_self = 1 if self_t and adj_to_set(nx, ny, self_t) else 0
        # If we can enter opponent territory, prioritize it (flipping enabled)
        enter_opp = 1 if (nx, ny) in opp_t else 0
        return (enter_opp * 50) - d_now + (0.15 * near_self) + (0.03 * (d_tgt - d_now))

    best = None
    best_sc = -10**18
    for dx, dy in moves:
        sc = step_score(dx, dy)
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]