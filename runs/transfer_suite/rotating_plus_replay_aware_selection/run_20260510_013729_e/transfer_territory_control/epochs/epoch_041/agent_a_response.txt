def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    x, y = observation.get("self_position") or [0, 0]
    x, y = int(x), int(y)

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

    def inb(px, py):
        return 0 <= px < w and 0 <= py < h

    def adj8(px, py):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = px + dx, py + dy
                if inb(nx, ny):
                    yield nx, ny

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp_pos = observation.get("opponent_position") or [w - 1, h - 1]
    opp_pos = (int(opp_pos[0]), int(opp_pos[1]))

    # Deterministic move ordering: stay, then N,NE,E,SE,S,SW,W,NW (prefers forward-ish toward top-left)
    moves = [(0, 0), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1)]

    best_move = (0, 0)
    best_sc = -10**9

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in blocks:
            continue

        near_opp = 0
        near_self = 0
        for ax, ay in adj8(nx, ny):
            if (ax, ay) in opp_terr:
                near_opp += 1
            if (ax, ay) in self_terr:
                near_self += 1

        if (nx, ny) in opp_terr:
            sc = 120 + 12 * near_opp + 4 * near_self - 0.5 * manh((nx, ny), opp_pos)
        elif (nx, ny) in unclaimed:
            sc = 45 + 9 * near_self - 7 * near_opp - 0.5 * manh((nx, ny), opp_pos)
        elif (nx, ny) in self_terr:
            sc = 15 + 6 * near_self - 2 * near_opp - 0.2 * manh((nx, ny), opp_pos)
        else:
            sc = 0

        # Mild pressure: if opponent has more territory, prioritize invasions; else expand near our territory.
        if observation.get("opponent_territory_count", 0) > observation.get("self_territory_count", 0):
            if (nx, ny) in opp_terr:
                sc += 40
        else:
            if (nx, ny) in unclaimed and near_self > 0:
                sc += 25

        if sc > best_sc:
            best_sc = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]