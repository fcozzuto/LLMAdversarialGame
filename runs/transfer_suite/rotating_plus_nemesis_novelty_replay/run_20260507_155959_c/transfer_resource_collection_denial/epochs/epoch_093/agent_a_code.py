def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if dx == 0 and dy == 0:
                moves.append((0, 0))
            else:
                if inb(nx, ny) and (nx, ny) not in obs:
                    moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        tx = w - 1 if ox < w // 2 else 0
        ty = h - 1 if oy < h // 2 else 0
        best = min(moves, key=lambda m: abs((sx + m[0]) - tx) + abs((sy + m[1]) - ty))
        return [best[0], best[1]]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Determine our "front" bias (toward our starting corner).
    front_x = 1 if sx >= (w - 1) / 2.0 else -1
    front_y = 1 if sy >= (h - 1) / 2.0 else -1

    # Pick a target where we are likely to arrive first; also bias toward our front.
    best_t = None
    best_k = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        front_bias = -0.15 * (front_x * (rx - sx) + front_y * (ry - sy))  # smaller is better
        # race_margin > 0 means we're closer
        race_margin = (od - sd)
        k = (race_margin, -sd, -front_bias, rx, ry)
        if best_k is None or k > best_k:
            best_k = k
            best_t = (rx, ry)
    tx, ty = best_t

    # Evaluate moves by (immediate progress + improving race margin).
    bestm = None
    bestm_k = None
    for dx, dy in moves:
        nsx, nsy = sx + dx, sy + dy
        sd2 = md(nsx, nsy, tx, ty)
        od2 = md(ox, oy, tx, ty)
        progress = -sd2
        race_after = (od2 - sd2)
        # tiny deterministic tie-break: prefer moving toward tx then ty
        k = (race_after, progress, -abs((nsx - tx)) - abs((nsy - ty)), dx, dy)
        if bestm_k is None or k > bestm_k:
            bestm_k = k
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]