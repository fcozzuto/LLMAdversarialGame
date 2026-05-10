def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    oppT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    opp_list = list(oppT)
    if not opp_list:
        opp_list = [(ox, oy)]
    def mdist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d_opp = 10**9
            for px, py in opp_list:
                t = abs(nx - px) + abs(ny - py)
                if t < d_opp:
                    d_opp = t
            in_opp = (nx, ny) in oppT
            in_un = (nx, ny) in unclaimed
            in_self = (nx, ny) in selfT
            # Big preference to enter opponent territory when possible; otherwise, press toward it.
            # Slight preference to take unclaimed near the opponent, avoid pointless self-blocking.
            score = 0
            score -= 500 if in_opp else 0
            score -= 20 * d_opp
            score -= 6 if in_un else 0
            score += 2 if in_self else 0
            # Encourage reducing distance to opponent position as a tie-breaker.
            score -= 0.5 * mdist((nx, ny), (ox, oy))
            cand.append((score, dx, dy))

    cand.sort(key=lambda t: (t[0], -abs(t[1]) - abs(t[2]), t[1], t[2]))
    return [int(cand[0][1]), int(cand[0][2])] if cand else [0, 0]