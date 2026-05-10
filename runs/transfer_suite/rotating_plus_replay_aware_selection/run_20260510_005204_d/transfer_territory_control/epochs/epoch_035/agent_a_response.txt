def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_unclaimed(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                c += 1
        return c

    def adj_opp(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in opp_terr:
                c += 1
        return c

    def corner_bias(x, y):
        # drive into unclaimed; slight preference to approach our own start corner
        # (stable deterministic bias to avoid cycling).
        if sx <= w // 2:
            cx = 0
        else:
            cx = w - 1
        if sy <= h // 2:
            cy = 0
        else:
            cy = h - 1
        return -(abs(x - cx) + abs(y - cy))

    best_move = (0, 0)
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        if (nx, ny) in unclaimed:
            base = 80
        elif (nx, ny) in opp_terr:
            base = 55  # flipping territory on entry
        elif (nx, ny) in self_terr:
            base = 10
        else:
            base = 5

        # expansion pressure
        score = base + 8 * adj_unclaimed(nx, ny) + 4 * adj_opp(nx, ny) + 1 * corner_bias(nx, ny)

        # discourages stepping onto currently opponent territory that is isolated (often loses tempo)
        if (nx, ny) in opp_terr and adj_opp(nx, ny) == 0 and adj_unclaimed(nx, ny) == 0:
            score -= 10

        # deterministic tie-break: prefer lexicographically smaller move
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]