def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_unclaimed(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                c += 1
        return c

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    un_list = list(unclaimed)[:64]
    if un_list:
        best = None
        for tx, ty in un_list:
            ds = manh(sx, sy, tx, ty)
            do = manh(ox, oy, tx, ty)
            gain = do - ds  # prefer cells closer to us than opponent
            tie = -adj_unclaimed(tx, ty)
            key = (gain, tie, tx, ty)
            if best is None or key > best[0]:
                best = (key, (tx, ty))
        tx, ty = best[1]
    else:
        targets = list(opp_terr)[:32] if opp_terr else []
        if targets:
            tx, ty = min(targets, key=lambda p: (manh(sx, sy, p[0], p[1]), p[0], p[1]))
        else:
            tx, ty = sx, sy

    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = 0
        if (nx, ny) in opp_terr:
            v += 10
        elif (nx, ny) in unclaimed:
            v += 8
        elif (nx, ny) in self_terr:
            v += 3
        v += 2 * adj_unclaimed(nx, ny)
        v += 0.8 * (manh(ox, oy, nx, ny) - manh(ox, oy, sx, sy))  # keep distance pressure
        v += -0.9 * manh(nx, ny, tx, ty)  # go to target
        if v > best_score or (v == best_score and (dx, dy) < best_move):
            best_score = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]