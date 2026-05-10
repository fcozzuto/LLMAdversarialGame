def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    x, y = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    try:
        x, y, ox, oy = int(x), int(y), int(ox), int(oy)
    except:
        x = y = ox = oy = 0

    def norm_pos(px, py):
        return int(px), int(py)

    x, y = norm_pos(x, y)
    ox, oy = norm_pos(ox, oy)

    blocks = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            try:
                blocks.add((int(p[0]), int(p[1])))
            except:
                pass

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            try:
                unclaimed.add((int(p[0]), int(p[1])))
            except:
                pass

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            try:
                opp_terr.add((int(p[0]), int(p[1])))
            except:
                pass

    self_terr = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            try:
                self_terr.add((int(p[0]), int(p[1])))
            except:
                pass

    def inb(a, b):
        return 0 <= a < w and 0 <= b < h

    if not inb(x, y):
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in blocks:
            continue

        md = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        score = -md

        if (nx, ny) in opp_terr:
            score += 5000
        if (nx, ny) in unclaimed:
            score += 1200
        if (nx, ny) in self_terr:
            score += 200

        # small tie-break: prefer closer to center of potential expansion (toward opponent)
        if best is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]