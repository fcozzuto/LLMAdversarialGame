def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

    opp_terr = set()
    for p in (observation.get("opponent_territory", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    self_terr = set()
    for p in (observation.get("self_territory", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in (observation.get("unclaimed_cells", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    ox, oy = int(ox), int(oy)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def adj_to_opp(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in opp_terr:
                    return True
        return False

    best_dx, best_dy = 0, 0
    best_val = -10**18

    # Prefer stepping into cells that touch opponent territory, or directly capture it.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in opp_terr:
            val = 60 - (abs(nx - ox) + abs(ny - oy))
        elif (nx, ny) in unclaimed:
            val = 12
            if adj_to_opp(nx, ny):
                val += 26
            # Push toward opponent side slightly (counter-sweeper interception)
            val += 2 * (-(abs(nx - ox) + abs(ny - oy)))
        elif (nx, ny) in self_terr:
            val = 4
        else:
            val = -5

        if dx == 0 and dy == 0:
            val -= 3

        # Mild tie-breaker: avoid walls/obstacles by preferring lower "risk"
        risk = 0
        for tx in (-1, 0, 1):
            for ty in (-1, 0, 1):
                if tx == 0 and ty == 0:
                    continue
                x2, y2 = nx + tx, ny + ty
                if not inb(x2, y2) or (x2, y2) in obstacles:
                    risk += 1
        val -= risk * 0.5

        if val > best_val:
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]