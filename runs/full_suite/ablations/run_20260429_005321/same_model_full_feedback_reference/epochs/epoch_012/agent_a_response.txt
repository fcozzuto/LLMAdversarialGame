def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            cand.append((dx, dy))

    if not cand:
        return [0, 0]

    me = (sx, sy)
    opp = (ox, oy)

    # Strategic change: evaluate each move by self-vs-opponent access to all remaining resources,
    # using a "best resource takeover" advantage rather than single-target chasing.
    best_score = None
    best_move = (0, 0)
    for dx, dy in cand:
        nm = (sx + dx, sy + dy)
        # Compute self and opponent distances to nearest resource; also accumulate limited advantage.
        self_near = 10**9
        opp_near = 10**9
        sorted_rs = []
        for r in resources:
            d1 = md(nm, r)
            d2 = md(opp, r)
            sorted_rs.append((d1, d2, r))
        if sorted_rs:
            # Nearest takeover metric
            for d1, d2, r in sorted_rs:
                if d1 < self_near:
                    self_near = d1
                if d2 < opp_near:
                    opp_near = d2
            # Focus on the closest few to reduce cost and increase determinism
            sorted_rs.sort(key=lambda t: (t[0], t[2][0], t[2][1]))
            top = sorted_rs[:4]
            takeover = 0
            for d1, d2, r in top:
                takeover += (d2 - d1) * 50 - d1 * 3
            # Add opponent proximity penalty to avoid getting "cut off"
            opp_close_pen = -md(nm, opp) * 2
            # Prefer fewer blocking escape routes: if opponent already closer to many, reduce score
            opp_adv_count = 0
            for d1, d2, r in top:
                if d2 < d1:
                    opp_adv_count += 1
            block_bias = -opp_adv_count * 15
            score = takeover + (opp_near - self_near) * 25 + opp_close_pen + block_bias
        else:
            # No resources known: move to increase distance from obstacles? just head away from opponent corner
            score = (md(nm, opp) * 2) - (nm[0] * 0 + nm[1] * 0)

        # Deterministic tie-break: prefer smaller dx/dy lexicographically, then coordinates
        key = (-(dx * 10 + dy), nm[0], nm[1])
        if best_score is None or score > best_score or (score == best_score and key < (-(best_move[0] * 10 + best_move[1]), sx + best_move[0], sy + best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]