def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    selfT = to_set("self_territory")
    oppT = to_set("opponent_territory")
    unclaimed = to_set("unclaimed_cells")

    cx, cy = (w - 1) // 2, (h - 1) // 2
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # nearest unclaimed target used as a weak attractor (keeps expansion instead of pure avoidance)
    if unclaimed:
        un_list = list(unclaimed)
        best_un = min(un_list, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
    else:
        best_un = (cx, cy)

    def frontier_bonus(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in selfT:
                    return 8
        return 0

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        # prefer claiming frontier cells (our territory expansion)
        score += frontier_bonus(nx, ny)

        # prefer taking/contesting opponent cells (flipping enabled)
        if (nx, ny) in oppT:
            score += 1200

        # control stability: avoid letting opponent immediately approach
        d_opp = abs(nx - ox) + abs(ny - oy)
        score += 0.8 * d_opp

        # medium-term direction: steer toward center while still expanding
        score += -0.6 * (abs(nx - cx) + abs(ny - cy))

        # weak pull to nearest unclaimed (unless it's essentially behind us)
        score += 0.5 * (-(abs(nx - best_un[0]) + abs(ny - best_un[1])))

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]