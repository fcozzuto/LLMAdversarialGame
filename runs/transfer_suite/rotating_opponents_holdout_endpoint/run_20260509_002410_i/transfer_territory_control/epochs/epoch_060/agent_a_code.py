def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))
    sx, sy, px, py = int(sx), int(sy), int(px), int(py)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    opp_terr = set()
    for c in observation.get("opponent_territory") or []:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h:
                opp_terr.add((x, y))

    unclaimed = []
    for c in observation.get("unclaimed_cells") or []:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                unclaimed.append((x, y))

    resources = []
    for c in observation.get("resources") or []:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    best = (0, (0, 0))
    moves = dirs + [(0, 0)]
    for dx, dy in dirs:
        x, y = sx + dx, sy + dy
        if not inb(x, y) or (x, y) in obs:
            continue
        if (x, y) in opp_terr:
            continue
        score = 0
        if resources:
            dmin = min(abs(x - rx) + abs(y - ry) for rx, ry in resources)
            score += 30 - 2 * dmin
        if unclaimed:
            dmin = min(abs(x - ux) + abs(y - uy) for ux, uy in unclaimed)
            score += 20 - 2 * dmin
        dp = abs(x - px) + abs(y - py)
        score += 2 * dp
        if (x, y) == (px, py):
            score -= 100
        if score > best[0] or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))
    dx, dy = best[1]
    return [int(dx), int(dy)]