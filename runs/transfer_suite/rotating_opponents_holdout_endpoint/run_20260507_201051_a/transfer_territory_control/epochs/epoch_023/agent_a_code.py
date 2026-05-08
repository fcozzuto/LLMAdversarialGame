def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    st = set(map(tuple, observation.get("self_territory") or []))
    ot = set(map(tuple, observation.get("opponent_territory") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    if (sx, sy) in obstacles:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick global anchors deterministically: prioritize near unclaimed/opponent cells.
    anchors = []
    if unclaimed:
        # Sample anchors by fixed ordering: sort by (dist to center, dist to self) then by coordinates.
        for x, y in sorted(unclaimed, key=lambda p: (abs(p[0] - cx) + abs(p[1] - cy), abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))[:10]:
            anchors.append((x, y))
    if not anchors and ot:
        for x, y in sorted(ot, key=lambda p: (abs(p[0] - cx) + abs(p[1] - cy), abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))[:10]:
            anchors.append((x, y))

    def anchor_best_dist(x, y):
        if not anchors:
            return abs(x - cx) + abs(y - cy)
        md = 10**9
        for ax, ay in anchors:
            d = abs(ax - x) + abs(ay - y)
            if d < md:
                md = d
        return md

    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = 0
        if (nx, ny) in ot:
            v += 220  # immediate steal pressure
            # encourage approaching boundary cell, not just any ot cell
        if (nx, ny) in unclaimed:
            v += 130  # secure neutral territory
        if (nx, ny) in st:
            v += 10   # safe continuity

        # Discourage stepping into opponent territory if no nearby upside (counterclaim defense)
        if (nx, ny) in ot and not unclaimed and st:
            v -= 35

        distc = abs(nx - cx) + abs(ny - cy)
        v += int(70 - 3.5 * distc)  # center preference (keeps mobility in long runs)

        # Gradient towards anchors / expansion front
        v += int(45 - 8 * anchor_best_dist(nx, ny))

        # If adjacent to opponent territory, boost staying on that front
        adj_ot = False
        for ex, ey in ((nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1), (nx-1, ny-1), (nx+1, ny-1), (nx-1, ny+1), (nx+1, ny+1)):
            if 0 <= ex < w and 0 <= ey < h and (ex, ey) in ot:
                adj_ot = True
                break
        if adj_ot:
            v += 65

        # Prefer not to drift away if staying put is already strong
        if dx == 0 and dy == 0:
            v += 8

        if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
            bestv = v
            best = [dx, dy]

    return [int(best[0]), int(best[1])]