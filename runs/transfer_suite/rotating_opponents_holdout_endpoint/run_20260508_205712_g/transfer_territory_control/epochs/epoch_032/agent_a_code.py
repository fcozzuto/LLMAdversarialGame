def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_count(cellset, x, y):
        c = 0
        for dx, dy in moves:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if (nx, ny) in cellset:
                c += 1
        return c

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    target_center = (w // 2, h // 2)
    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        s = 0
        if (nx, ny) in self_terr:
            s += 4
        elif (nx, ny) in opp_terr:
            s += 24 + 3 * adj_count(opp_terr, nx, ny)
        elif (nx, ny) in unclaimed:
            s += 14 + 2 * adj_count(self_terr, nx, ny)
        else:
            s += 1

        s += 2 * adj_count(self_terr, nx, ny)
        s -= 1.5 * adj_count(opp_terr, nx, ny)
        s += 0.5 * (9 - dist_cheb(nx, ny, target_center[0], target_center[1]))
        s -= 0.2 * dist_cheb(nx, ny, ox, oy)

        if (dx, dy) == (0, 0):
            s -= 1.0
        if s > best_score or (s == best_score and (dx, dy) < best_move):
            best_score = s
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]