def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def tupset(key):
        out = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                out.add((int(p[0]), int(p[1])))
        return out

    self_ter = tupset("self_territory")
    opp_ter = tupset("opponent_territory")
    unclaimed = tupset("unclaimed_cells")
    obstacles = tupset("obstacles")

    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0.0
        if (nx, ny) in self_ter:
            val += 6.0
        elif (nx, ny) in unclaimed:
            val += 11.0
        elif (nx, ny) in opp_ter:
            val += 16.0

        # Prefer expanding near our territory and away from the opponent.
        if val > 0:
            val += -0.35 * man(nx, ny, ox, oy)

        # Soft preference: if near opponent territory, prefer flipping only when it is unclaimed/opp; otherwise back off.
        near_opp = 0
        for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            px, py = nx + ax, ny + ay
            if (px, py) in opp_ter:
                near_opp += 1
        val += 0.8 * near_opp if (nx, ny) in opp_ter else -0.3 * near_opp

        # Small obstacle proximity penalty
        near_obs = 0
        for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            px, py = nx + ax, ny + ay
            if (px, py) in obstacles:
                near_obs += 1
        val -= 0.2 * near_obs

        if val > best_val + 1e-9:
            best_val = val
            best_move = [dx, dy]

    return best_move