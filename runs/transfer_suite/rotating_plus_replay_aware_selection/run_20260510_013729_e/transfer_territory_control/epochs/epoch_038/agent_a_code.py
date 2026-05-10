def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                s.add((int(p[0]), int(p[1])))
        return s

    blocks = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")
    opp_pos = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny):
                    yield nx, ny

    best_move = (0, 0)
    best_sc = -10**18

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocks:
            continue

        sc = 0
        if (nx, ny) in self_terr:
            sc += 2
        if (nx, ny) in unclaimed:
            sc += 10
            if any((ax, ay) in opp_terr for ax, ay in adj8(nx, ny)):
                sc += 6
        if (nx, ny) in opp_terr:
            sc -= 20
            if any((ax, ay) in self_terr for ax, ay in adj8(nx, ny)):
                sc += 14
            if any((ax, ay) in unclaimed for ax, ay in adj8(nx, ny)):
                sc += 6

        self_adj = 0
        opp_adj = 0
        uncl_adj = 0
        for ax, ay in adj8(nx, ny):
            if (ax, ay) in self_terr:
                self_adj += 1
            elif (ax, ay) in opp_terr:
                opp_adj += 1
            elif (ax, ay) in unclaimed:
                uncl_adj += 1
        sc += 2 * self_adj
        sc += 2 * uncl_adj
        sc += 1 * opp_adj

        # Keep pressure without suicidal chase: prefer moving away from opponent slightly.
        dist_opp = abs(nx - ox) + abs(ny - oy)
        sc += max(-8, min(8, dist_opp - (abs(sx - ox) + abs(sy - oy))))

        # Prefer center over edges when tied.
        sc += -0.05 * (abs(nx - cx) + abs(ny - cy))

        if sc > best_sc or (sc == best_sc and (dx, dy) < best_move):
            best_sc = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]