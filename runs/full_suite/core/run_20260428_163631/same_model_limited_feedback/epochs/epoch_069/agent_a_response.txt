def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obs = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]

    def inb(a, b): return 0 <= a < w and 0 <= b < h
    def dist(a, b, c, d): return abs(a - c) + abs(b - d)

    # Choose best resource: maximize advantage over opponent, then minimize our distance
    best = None
    if resources:
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            d_self = dist(x, y, rx, ry)
            d_opp = dist(ox, oy, rx, ry)
            score = (d_opp - d_self, -d_self)  # higher better
            if best is None or score > best[0]:
                best = (score, rx, ry)

    if best is None:
        # Fallback: go to center
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        _, tx, ty = best

    # Greedy one-step toward target with obstacle avoidance
    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            cand.append((dist(nx, ny, tx, ty), dx, dy))
    if not cand:
        return [0, 0]

    # Prefer smallest distance; tie-break deterministically by dx,dy order
    cand.sort(key=lambda t: (t[0], t[1], t[2]))
    return [int(cand[0][1]), int(cand[0][2])]