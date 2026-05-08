def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    if not resources:
        target = (w // 2, h // 2) if (w // 2, h // 2) not in obstacles else (ox, oy)
    else:
        best = None
        bestd = 10**9
        for r in resources:
            if r in obstacles:
                continue
            d = abs(r[0] - sx) + abs(r[1] - sy)
            if r in opp_terr:
                d += 2  # discourage
            if d < bestd or (d == bestd and (best is None or r < best)):
                bestd = d
                best = r
        target = best if best is not None else (w // 2, h // 2)

    moves = [(dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
    bestm = (0, 0)
    bestscore = 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dist = abs(target[0] - nx) + abs(target[1] - ny)
        score = dist
        if (nx, ny) in self_terr:
            score -= 1
        if (nx, ny) in opp_terr:
            score += 3
        if score < bestscore or (score == bestscore and (dx, dy) < bestm):
            bestscore = score
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]