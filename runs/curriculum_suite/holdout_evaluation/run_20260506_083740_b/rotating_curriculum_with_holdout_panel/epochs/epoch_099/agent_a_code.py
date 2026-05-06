def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves_sorted = moves
    best = (None, -10**18, 10**18)  # (move, value, self_dist)
    for dx, dy in moves_sorted:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        best_res = None
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Advantage: become closer than opponent, penalize being farther.
            val = (od - sd) * 100 - sd
            # Small preference for resources nearer to us (helps finish)
            if best_res is None or val > best_res[0] or (val == best_res[0] and sd < best_res[1]):
                best_res = (val, sd)
        # Also consider "blocking": avoid moves that let opponent immediately reach our chosen best.
        # Approximate with current opponent distance to our nearest resource from next cell.
        approx_block = best_res[1] if best_res else 0
        total = best_res[0] - approx_block * 0.5
        if total > best[1] or (total == best[1] and best_res[1] < best[2]):
            best = ((dx, dy), total, best_res[1])

    if best[0] is None:
        return [0, 0]
    dx, dy = best[0]
    return [dx, dy]