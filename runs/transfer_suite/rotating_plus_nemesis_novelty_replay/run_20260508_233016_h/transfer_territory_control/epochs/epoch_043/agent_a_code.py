def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def neigh8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        yield nx, ny

    opp_cells_adj_unclaimed = []
    for ux, uy in unclaimed:
        for nx, ny in neigh8(ux, uy):
            if (nx, ny) in opp_terr:
                opp_cells_adj_unclaimed.append((ux, uy))
                break

    target = None
    if opp_cells_adj_unclaimed:
        target = min(opp_cells_adj_unclaimed, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
    elif unclaimed:
        target = min(unclaimed, key=lambda c: (c[0] == 0 or c[0] == w - 1 or c[1] == 0 or c[1] == h - 1, abs(c[0] - sx) + abs(c[1] - sy)))
    else:
        cx, cy = w // 2, h // 2
        target = (cx, cy)

    best_move = [0, 0]
    best_val = -10**18
    tx, ty = target

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)

        val = 0.0
        if cell in unclaimed:
            val += 4.0
        if cell in self_terr:
            val += 0.8
        if cell in opp_terr:
            val += 2.6  # flipping on entry

        if any((px, py) in opp_terr for px, py in neigh8(nx, ny)):
            val += 2.0  # fight counterclaims on their front
        if any((px, py) in self_terr for px, py in neigh8(nx, ny)):
            val += 0.6  # keep expansion stable

        val += 0.45 * (-(abs(nx - tx) + abs(ny - ty)))  # deterministic pursuit
        val -= 0.3 if cell in opp_terr else 0.0

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move if best_move in moves else [0, 0]