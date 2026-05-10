def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    self_count = observation.get("self_territory_count", len(self_terr))
    opp_count = observation.get("opponent_territory_count", len(opp_terr))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def neighbors8(p):
        x, y = p
        out = []
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                out.append((nx, ny))
        return out

    def front(base):
        out = set()
        for p in base:
            for q in neighbors8(p):
                if q in unclaimed:
                    out.add(q)
        return out

    self_front = front(self_terr) if self_terr else set()
    opp_front = front(opp_terr) if opp_terr else set()

    # Choose strategic target deterministically
    going_defensive = opp_count > self_count
    if going_defensive and opp_front:
        target_set = opp_front
    elif self_front:
        target_set = self_front
    else:
        target_set = unclaimed if unclaimed else (set() if not self_terr else self_terr)

    if not target_set:
        return [0, 0]

    # Pick closest target with deterministic tie-break
    tx, ty = min(target_set, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[1], p[0]))

    best = None
    best_score = None
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)
        score = 0
        if cell in opp_terr:
            score += 500  # direct counter-claim
        elif cell in unclaimed:
            score += 120  # expand into new territory
        elif cell in self_terr:
            score += 20   # consolidation
        else:
            score += 5

        dtarget = abs(nx - tx) + abs(ny - ty)
        score -= 3 * dtarget

        # Avoid letting opponent get closer too quickly when we're not winning
        if not going_defensive:
            d_op = abs(nx - ox) + abs(ny - oy)
            score += -0.5 * d_op
        else:
            d_op = abs(nx - ox) + abs(ny - oy)
            score += 0.25 * d_op

        # Deterministic tie-break: prefer staying if equally good, else smallest dx, then dy
        cand = (score, -1 if (dx == 0 and dy == 0) else 0, -dx, -dy)
        if best is None or cand > best_score:
            best_score = cand
            best = [dx, dy]

    return best if best is not None else [0, 0]