def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_t = set()
    for c in observation.get("self_territory") or []:
        if c and len(c) >= 2:
            self_t.add((int(c[0]), int(c[1])))

    opp_t = set()
    for c in observation.get("opponent_territory") or []:
        if c and len(c) >= 2:
            opp_t.add((int(c[0]), int(c[1])))

    unclaimed = set()
    for c in observation.get("unclaimed_cells") or []:
        if c and len(c) >= 2:
            unclaimed.add((int(c[0]), int(c[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    center_x, center_y = w // 2, h // 2

    best = (None, -10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = 0
        if (nx, ny) in unclaimed:
            val += 12
        if (nx, ny) in self_t:
            val += 4
        if (nx, ny) in opp_t:
            val -= 18
        val += -abs(nx - ox) - abs(ny - oy) // 3
        val += -(abs(nx - center_x) + abs(ny - center_y)) // 4
        if val > best[1] or (val == best[1] and (dx, dy) == (0, 0)):
            best = ((dx, dy), val)

    return [best[0][0], best[0][1]]