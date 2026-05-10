def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    opp_pos = tuple(observation["opponent_position"])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_val = -10**18
    best = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0

        cell = (nx, ny)
        val = 0.0

        if cell in self_terr:
            val += 0.2
        if cell in unclaimed:
            val += 2.2
        if cell in opp_terr:
            val += 2.6 - 0.01 * man(nx, ny, opp_pos[0], opp_pos[1])

        # Encourage pushing frontier toward nearest unclaimed, and toward opponent for flips
        if unclaimed:
            # sample a few closest deterministically (no randomness)
            dlist = sorted(((man(nx, ny, c[0], c[1]), c) for c in unclaimed))[:6]
            if dlist:
                val += max(0.0, 1.6 - 0.02 * dlist[0][0])
        val += 0.001 * (-man(nx, ny, opp_pos[0], opp_pos[1]))

        # Avoid stepping into a crowded-opponent region unless unclaimed/flip is strong
        if cell in opp_terr and unclaimed:
            val -= 0.2

        # Prefer progress vs staying
        if (dx, dy) != (0, 0):
            val += 0.05

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]