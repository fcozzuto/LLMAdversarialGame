def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    parity = int(observation.get("turn_index", 0) or 0) & 1

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_unclaimed(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if in_bounds(nx, ny) and (nx, ny) in unclaimed:
                    return True
        return False

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        in_un = (nx, ny) in unclaimed
        in_opp = (nx, ny) in opp_terr
        in_self = (nx, ny) in self_terr
        adj_u = adj_unclaimed(nx, ny)

        dist_opp = abs(nx - ox) + abs(ny - oy)
        score = 0
        score += 260 if in_un else 0
        score += 160 if in_opp else 0
        score += 25 if in_self else 0
        score += 55 if adj_u else 0

        # Territory control: stay meaningful and avoid getting countered
        if parity == 0:
            score += -18 if dist_opp <= 1 else 0
            score += -dist_opp
        else:
            score += -10 if in_opp else 0
            score += -2 * dist_opp

        # Encourage forward progress from corners
        score += (nx + ny) * 0.5 if (sx + sy) <= (w - 1 + h - 1 - (sx + sy)) else 0

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]