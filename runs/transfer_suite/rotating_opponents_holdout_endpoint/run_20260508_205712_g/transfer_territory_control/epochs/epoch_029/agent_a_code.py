def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb_dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def count_unclaimed_nbr(x, y):
        c = 0
        for dx, dy in moves:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if (nx, ny) in unclaimed:
                c += 1
        return c

    base_d_opp = cheb_dist(sx, sy, ox, oy)
    best_val = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = 0.0
        d_opp = cheb_dist(nx, ny, ox, oy)
        val += 0.3 * (base_d_opp - d_opp)  # prefer approaching opponent

        if (nx, ny) in opp_terr:
            val += 20.0
            val += -1.5 * d_opp
        elif (nx, ny) in unclaimed:
            val += 10.0
            val += -1.0 * d_opp
        elif (nx, ny) in self_terr:
            val += 2.0
        else:
            val += 1.0 - 0.2 * d_opp

        val += 0.7 * count_unclaimed_nbr(nx, ny)
        if dx == 0 and dy == 0:
            val -= 0.2  # avoid stalling when alternatives exist

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]