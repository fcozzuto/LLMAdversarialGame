def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    self_t = set()
    for c in observation.get("self_territory") or []:
        if c and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if inb(x, y):
                self_t.add((x, y))
    opp_t = set()
    for c in observation.get("opponent_territory") or []:
        if c and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if inb(x, y):
                opp_t.add((x, y))
    unclaimed = set()
    for c in observation.get("unclaimed_cells") or []:
        if c and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if inb(x, y):
                unclaimed.add((x, y))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if (0, 0) not in moves:
        moves.append((0, 0))

    def neigh_cells(x, y):
        return [(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    best = (None, -10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles or not inb(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        # Base priorities: take opponent territory strongly, expand into unclaimed, otherwise advance toward opponent.
        val = 0
        if (nx, ny) in opp_t:
            val += 1000
        elif (nx, ny) in unclaimed:
            val += 250
        elif (nx, ny) in self_t:
            val -= 5

        # Tactical: prefer moves that are adjacent to opponent territory (likely to flip next).
        adj_opp = 0
        for ax, ay in neigh_cells(nx, ny):
            if (ax, ay) in opp_t:
                adj_opp += 1
        val += adj_opp * 18

        # Tactical: avoid being adjacent to obstacles.
        adj_obs = 0
        for ax, ay in neigh_cells(nx, ny):
            if (ax, ay) in obstacles:
                adj_obs += 1
        val -= adj_obs * 6

        # Progress: reduce distance to opponent position.
        val += -(abs(nx - ox) + abs(ny - oy)) * 3

        # Tie-break deterministically toward closer to unclaimed/opponent boundary.
        if val > best[1]:
            best = ((dx, dy), val)

    dx, dy = best[0] if best[0] is not None else (0, 0)
    return [int(dx), int(dy)]