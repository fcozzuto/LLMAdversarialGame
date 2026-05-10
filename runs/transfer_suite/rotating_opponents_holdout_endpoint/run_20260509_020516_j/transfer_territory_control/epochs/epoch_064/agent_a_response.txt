def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def to_set(v):
        s = set()
        if v:
            for p in v:
                if p and len(p) >= 2:
                    x, y = int(p[0]), int(p[1])
                    if inb(x, y):
                        s.add((x, y))
        return s

    obstacles = to_set(observation.get("obstacles"))
    unclaimed = to_set(observation.get("unclaimed_cells"))
    my_t = to_set(observation.get("self_territory"))
    opp_t = to_set(observation.get("opponent_territory"))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (-(10**9), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine would keep in place; score as staying
        cell = (nx, ny)

        # Base claim value
        if cell in opp_t:
            val = 3.5
        elif cell in unclaimed:
            val = 2.5
        elif cell in my_t:
            val = 1.0
        else:
            val = 1.1  # other/unknown but not obstacle

        # Frontier pressure: encourage moving closer to opponent position + opponent frontier
        d_opp = abs(nx - ox) + abs(ny - oy)
        val += 0.02 * (-d_opp)

        # If we are adjacent to opponent territory, strongly prefer that direction
        adj = False
        for adx, ady in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            ax, ay = nx + adx, ny + ady
            if (ax, ay) in opp_t:
                adj = True
                break
        if adj:
            val += 1.3

        # Small anti-cycling: prefer moves that change position (deterministic)
        if (dx, dy) != (0, 0):
            val += 0.05

        # Deterministic tie-break by dx,dy order
        key = (val, -dx, -dy)
        if key > (best[0], -best[1], -best[2]):
            best = (val, dx, dy)

    return [int(best[1]), int(best[2])]