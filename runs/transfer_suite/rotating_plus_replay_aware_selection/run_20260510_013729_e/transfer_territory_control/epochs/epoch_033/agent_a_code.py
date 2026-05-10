def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    x, y = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocks = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            try:
                blocks.add((int(p[0]), int(p[1])))
            except:
                pass

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            try:
                opp_terr.add((int(p[0]), int(p[1])))
            except:
                pass

    res = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            try:
                res.append((int(p[0]), int(p[1])))
            except:
                pass

    terr_self = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            try:
                terr_self.add((int(p[0]), int(p[1])))
            except:
                pass

    def in_bounds(px, py):
        return 0 <= px < w and 0 <= py < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in blocks:
            continue
        score = 0
        if (nx, ny) in opp_terr and (nx, ny) not in terr_self:
            score -= 100000
        if res:
            md = 10**9
            for rx, ry in res:
                d = abs(rx - nx) + abs(ry - ny)
                if d < md:
                    md = d
            score += 5000 - md * 10
        score += -abs(nx - ox) - abs(ny - oy)
        score += 2 if (nx, ny) in terr_self else 0
        if (best is None) or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]