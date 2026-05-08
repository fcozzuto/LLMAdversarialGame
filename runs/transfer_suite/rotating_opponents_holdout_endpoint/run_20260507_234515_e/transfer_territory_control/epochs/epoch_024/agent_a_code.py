def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    cx, cy = w // 2, h // 2

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        a = a - c
        if a < 0: a = -a
        b = b - d
        if b < 0: b = -b
        return a + b

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        d_opp = man(nx, ny, ox, oy)
        d_ctr = man(nx, ny, cx, cy)
        cell = (nx, ny)

        if cell in opp_terr:
            type_bonus = 70
        elif cell in unclaimed:
            type_bonus = 28
        elif cell in self_terr:
            type_bonus = 6
        else:
            type_bonus = 10

        # Prefer securing center while pressuring opponent cells (edge-claim tends to skimp center).
        score = type_bonus + (50 - d_opp) - 0.6 * d_ctr

        # Mild anti-stall: discourage staying unless it improves position relative to center/opp.
        if dx == 0 and dy == 0:
            score -= 6 + 0.3 * (man(sx, sy, cx, cy) - d_ctr) + 0.2 * (man(sx, sy, ox, oy) - d_opp)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]