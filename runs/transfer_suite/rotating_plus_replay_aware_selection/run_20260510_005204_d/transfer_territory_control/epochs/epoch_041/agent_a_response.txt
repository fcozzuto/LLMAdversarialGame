def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_terr = set()
    for p in (observation.get("self_territory") or []):
        if p and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_count(x, y, s):
        c = 0
        for dx, dy in moves:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in s:
                c += 1
        return c

    def corner_bias(x, y):
        # encourage carving outward when ahead, keep safe when behind
        d1 = abs(x - 0) + abs(y - 0)
        d2 = abs(x - (w - 1)) + abs(y - (h - 1))
        return d1 - d2  # our corner is (0,0), opponent is (w-1,h-1)

    ahead = int(observation.get("self_territory_count", 0)) >= int(observation.get("opponent_territory_count", 0))
    aggressive = not ahead

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        score = 0
        if (nx, ny) in opp_terr:
            score += 1000 if aggressive else 900
        elif (nx, ny) in unclaimed:
            score += 120 if aggressive else 160
        elif (nx, ny) in self_terr:
            score += 10 if aggressive else 20
        else:
            score += 0

        score += 7 * adj_count(nx, ny, unclaimed)
        score += 4 * adj_count(nx, ny, opp_terr)
        score += -6 * adj_count(nx, ny, self_terr) if aggressive else 0

        tx, ty = w - 1, h - 1
        sx_t, sy_t = 0, 0
        if aggressive:
            # push toward opponent when attacking; otherwise keep expanding
            target_dist = abs(nx - tx) + abs(ny - ty)
            score += 70 - target_dist
        else:
            target_dist = abs(nx - sx_t) + abs(ny - sy_t)
            score += target_dist * 0.1
            score += 3 * (corner_bias(nx, ny) > 0)

        # deterministic tie-break: lowest (score, dx, dy) replaced by higher score
        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]