def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_pos = observation.get("opponent_position", (w - 1, h - 1))
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_count(cell, terrset):
        x, y = cell
        c = 0
        for dx, dy in dirs[:-1]:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in terrset:
                c += 1
        return c

    def cell_priority(x, y):
        if not inb(x, y) or (x, y) in obstacles:
            return -10**9
        d = abs(x - sx) + abs(y - sy)
        edge = min(x, y, w - 1 - x, h - 1 - y)
        un = 1.0 if (x, y) in unclaimed else 0.0
        mine_adj = adj_count((x, y), self_terr)
        opp_adj = adj_count((x, y), opp_terr)
        cont = 0.0
        if (x, y) in opp_terr:
            cont = 4.5  # prefer flipping back
        # prefer expanding pockets, contest near opponent, avoid edges
        return (un * 10.0 + cont + 1.6 * mine_adj - 0.9 * opp_adj + 0.25 * (8 - edge) + 0.08 * (8 - d) - 0.02 * abs(x - ox) - 0.02 * abs(y - oy))

    best_move = [0, 0]
    best_val = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        v = cell_priority(nx, ny)
        if v > best_val:
            best_val = v
            best_move = [dx, dy]

    if best_move == [0, 0]:
        # fallback: head toward nearest high-priority unclaimed
        targets = list(unclaimed) if unclaimed else list(opp_terr)
        if not targets:
            return [0, 0]
        tx, ty = min(targets, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        # validate fallback step; if obstacle, stay
        if inb(sx + dx, sy + dy) and (sx + dx, sy + dy) not in obstacles:
            return [dx, dy]
        return [0, 0]
    return best_move