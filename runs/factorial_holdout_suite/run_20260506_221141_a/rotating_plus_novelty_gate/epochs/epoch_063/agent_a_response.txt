def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(a, b, c, d):
        dx, dy = abs(a - c), abs(b - d)
        return dx if dx > dy else dy  # Chebyshev

    # Choose resource where we beat opponent by largest margin; break ties by proximity and center bias.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_key = None
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        beat = od - sd  # positive means we can arrive no later
        center_bias = - (abs(rx - cx) + abs(ry - cy))  # closer to center better
        parity_bias = 0
        if (ry % 2) == (sy % 2):
            parity_bias = 0.5  # helps against row-sweep patterns
        key = (beat, -sd, center_bias + parity_bias)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        nd = dist(nx, ny, tx, ty)
        # Prefer stepping onto resources; otherwise greedy to target.
        res_bonus = 0
        if (nx, ny) in set(resources):
            res_bonus = 10
        # Small preference to avoid giving opponent advantage: reduce distance gap if close.
        gap = dist(ox, oy, tx, ty) - nd
        val = (gap, -nd, res_bonus)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]