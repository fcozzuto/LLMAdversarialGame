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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def unclaimed_nbr(x, y):
        c = 0
        for dx, dy in moves:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if (nx, ny) in unclaimed:
                c += 1
        return c

    cx, cy = w // 2, h // 2
    best = (-10**18, (0, 0))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        val = 0
        if (nx, ny) in self_terr:
            val += 1
        elif (nx, ny) in unclaimed:
            val += 3 + 0.7 * unclaimed_nbr(nx, ny)
        elif (nx, ny) in opp_terr:
            val += 6 + 0.2 * unclaimed_nbr(nx, ny)
        else:
            val += 0.2

        # Tactical: get closer to the center early, but prioritize counterclaim near opponent
        dist_center = cheb(nx, ny, cx, cy)
        val -= 0.12 * dist_center
        val += 0.08 * (cheb(nx, ny, ox, oy) * -1)  # prefer moving away if already strong
        if (nx, ny) in opp_terr:
            val += 0.08 * (10 - cheb(nx, ny, ox, oy))

        # Frontier pressure: prefer expanding from boundary of our territory
        if (nx, ny) not in self_terr:
            b = 0
            for adx, ady in moves:
                tx, ty = nx + adx, ny + ady
                if (tx, ty) in self_terr:
                    b += 1
            val += 0.6 * b

        if val > best[0] or (val == best[0] and (dx, dy) < best[1]):
            best = (val, (dx, dy))
    return [int(best[1][0]), int(best[1][1])]