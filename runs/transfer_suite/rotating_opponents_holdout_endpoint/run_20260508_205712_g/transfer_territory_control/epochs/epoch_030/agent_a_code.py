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
    cx, cy = w // 2, h // 2

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def unclaimed_nbr_count(x, y):
        c = 0
        for dx, dy in moves:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if (nx, ny) in unclaimed:
                c += 1
        return c

    best_val = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        v = 0
        if (nx, ny) in unclaimed:
            v += 6 + 0.5 * unclaimed_nbr_count(nx, ny)
        elif (nx, ny) in opp_terr:
            v += 4.5 + 0.25 * unclaimed_nbr_count(nx, ny)
        elif (nx, ny) in self_terr:
            v += 1.0
        else:
            v += 0.3

        # Prefer taking ground toward the board center and away from the opponent.
        v += 1.2 * (cheb(ox, oy, nx, ny) - cheb(ox, oy, sx, sy))
        v += 0.9 * (cheb(nx, ny, cx, cy) - cheb(sx, sy, cx, cy)) * (-1)

        # Slightly prefer diagonal/advancing moves over staying still.
        if dx != 0 or dy != 0:
            v += 0.05

        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]