def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def to_set(key):
        s = set()
        for p in observation.get(key, []) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    self_terr = to_set("self_territory")
    opp_terr = to_set("opponent_territory")
    resources = to_set("resources")

    oppp = observation.get("opponent_position", None) or [None, None]
    ox, oy = (int(oppp[0]), int(oppp[1])) if oppp[0] is not None and oppp[1] is not None else (None, None)

    self_cnt = int(observation.get("self_territory_count", 0) or 0)
    opp_cnt = int(observation.get("opponent_territory_count", 0) or 0)
    behind = self_cnt < opp_cnt

    if unclaimed:
        tx, ty = min(unclaimed, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    elif resources:
        tx, ty = min(resources, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    else:
        tx, ty = w // 2, h // 2

    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in unclaimed:
            score += 200 if behind else 120
        if (nx, ny) in opp_terr:
            score -= 220
        if (nx, ny) in self_terr:
            score += 20
        if (nx, ny) in resources:
            score += 60

        d = abs(nx - tx) + abs(ny - ty)
        score -= 3 * d

        if ox is not None:
            dd = abs(nx - ox) + abs(ny - oy)
            score -= 2 * dd if behind else -1 * dd

        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        best = (0, 0)
        if (sx, sy) in obstacles:
            for dx, dy in moves:
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    best = (dx, dy)
                    break
    return [int(best[0]), int(best[1])]