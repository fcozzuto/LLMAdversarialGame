def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))

    unclaimed = [(int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []) if 0 <= int(x) < w and 0 <= int(y) < h and (int(x), int(y)) not in obstacles]

    def md(a, b, c, d):
        dx = a - c
        dy = b - d
        return (dx if dx >= 0 else -dx) + (dy if dy >= 0 else -dy)

    tx, ty = ox, oy
    if unclaimed:
        best = None
        for x, y in unclaimed:
            ds = md(sx, sy, x, y)
            do = md(ox, oy, x, y)
            # prefer cells closer to us than opponent, but not too far
            score = (ds - do) * 10 + ds
            if best is None or score < best[0]:
                best = (score, x, y)
        tx, ty = best[1], best[2]

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    bestm = None
    bestscore = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        dist_to_target = md(nx, ny, tx, ty)

        cell_bonus = 0
        if (nx, ny) in opp_terr:
            cell_bonus += 120  # likely flip on entry
        elif (nx, ny) not in self_terr:
            cell_bonus += 30   # entering unclaimed or contested
        elif (nx, ny) in self_terr:
            cell_bonus += 0

        # also avoid letting opponent get closer to target
        opp_dist = md(ox, oy, tx, ty)
        my_dist = dist_to_target
        relative = opp_dist - my_dist

        score = cell_bonus + relative * 5 - my_dist
        if bestscore is None or score > bestscore:
            bestscore = score
            bestm = (dx, dy)

    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]