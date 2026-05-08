def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    my = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unq = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if (0, 0) not in moves: moves.append((0, 0))

    # Deterministic preference order
    moves = sorted(moves, key=lambda t: (t[0], t[1]))

    def score_cell(x, y):
        if not inb(x, y) or (x, y) in blocked:
            return -10**9
        d_opp = abs(x - ox) + abs(y - oy)
        near_factor = -2 if d_opp <= 2 else (0 if d_opp <= 4 else 1)
        s = 0
        if (x, y) in unq: s += 30
        if (x, y) in my: s += 8
        if (x, y) in opp: s -= 18  # flipping helps, but opponent-controlled is risky to contest
        # Encourage expansion toward unclaimed while avoiding close contact
        if unq:
            # small deterministic "nearest unclaimed" estimate from current step
            bestd = 10**9
            for ux, uy in unq:
                dd = abs(ux - x) + abs(uy - y)
                if dd < bestd:
                    bestd = dd
                    if bestd == 0: break
            s += max(0, 18 - 3 * bestd)
        s += near_factor * (6 if d_opp <= 2 else 3) + d_opp  # generally prefer distance from opponent
        return s

    best_move = (0, 0)
    best_score = score_cell(sx, sy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sc = score_cell(nx, ny)
        if sc > best_score:
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]