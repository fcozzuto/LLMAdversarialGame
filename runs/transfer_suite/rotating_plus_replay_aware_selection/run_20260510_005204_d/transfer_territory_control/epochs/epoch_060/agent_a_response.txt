def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    nbrs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def count_adj(cellset, x, y):
        c = 0
        for dx, dy in nbrs:
            if (x + dx, y + dy) in cellset:
                c += 1
        return c

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in self_terr:
            val = 1 + count_adj(self_terr, nx, ny) * 2
        elif (nx, ny) in opp_terr:
            val = 80 + count_adj(self_terr, nx, ny) * 3 - count_adj(opp_terr, nx, ny) * 1
        elif (nx, ny) in unclaimed:
            val = 55 + count_adj(self_terr, nx, ny) * 6 + count_adj(opp_terr, nx, ny) * 3
        else:
            val = 2

        # Prefer forward expansion and also reduce opponent closeness
        d_to_opp = manh(nx, ny, ox, oy)
        val += max(0, 24 - d_to_opp) * 0.5

        # Encourage moves that open more unclaimed around us
        val += count_adj(unclaimed, nx, ny) * 1.5

        key = (val, -manh(nx, ny, 7, 7), -manh(nx, ny, 0, 7), -manh(nx, ny, 7, 0), -dx, -dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    return best[1] if best is not None else [0, 0]