def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    oxp = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(oxp[0]), int(oxp[1])

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    unclaimed = set()
    for t in observation.get("unclaimed_cells") or []:
        if t is not None and len(t) >= 2:
            unclaimed.add((int(t[0]), int(t[1])))

    oppT = set()
    for t in observation.get("opponent_territory") or []:
        if t is not None and len(t) >= 2:
            oppT.add((int(t[0]), int(t[1])))

    resources = set()
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            resources.add((int(r[0]), int(r[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0, -10**9)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue

        md_opp = abs(nx - ox) + abs(ny - oy)
        score = 0
        if (nx, ny) in resources:
            score += 6
        if (nx, ny) in unclaimed:
            score += 3
        if (nx, ny) in oppT:
            score -= 5
        if md_opp <= 2:
            score -= (3 - md_opp) * 2

        if resources:
            mind = 10**9
            for rx, ry in resources:
                d = abs(nx - rx) + abs(ny - ry)
                if d < mind:
                    mind = d
            score += max(0, 4 - mind)

        if (score, -dx, -dy) > (best[2], -best[0], -best[1]):
            best = (dx, dy, score)
        elif score == best[2] and (dx, dy) < (best[0], best[1]):
            best = (dx, dy, score)

    return [int(best[0]), int(best[1])]