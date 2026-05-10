def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2]
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if unclaimed:
        cx = sum(x for x, _ in unclaimed) / len(unclaimed)
        cy = sum(y for _, y in unclaimed) / len(unclaimed)
    else:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    opp_corner = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(opp_corner[0]), int(opp_corner[1])

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def adj_obst(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    c += 1
        return c

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in unclaimed:
            score += 12
        if (nx, ny) in op_terr:
            score += 7
        if (nx, ny) in self_terr:
            score += 3

        dist_cent = abs(nx - cx) + abs(ny - cy)
        dist_src = abs(sx - cx) + abs(sy - cy)
        score += (dist_src - dist_cent) * 2

        if unclaimed:
            dmin = None
            for tx, ty in unclaimed:
                d = abs(nx - tx) + abs(ny - ty)
                if dmin is None or d < dmin:
                    dmin = d
                    if dmin == 0:
                        break
            if dmin is not None:
                score += max(0, 8 - dmin)
        score -= adj_obst(nx, ny) * 1.5

        # Slight bias to move away from own tail when possible: stay closer to opponent corner breaks symmetry less often
        score += -(abs(nx - ox) + abs(ny - oy)) * 0.05

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]