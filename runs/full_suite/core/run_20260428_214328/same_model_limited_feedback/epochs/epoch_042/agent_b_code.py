def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def inb(px, py):
        return 0 <= px < w and 0 <= py < h

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return abs(dx) + abs(dy)

    # Choose a target resource that we can contest: closest adjusted by opponent closeness.
    cx = ox - (w - 1 - x)  # deterministic mild bias toward center-ish
    best_t = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = dist(x, y, rx, ry)
        opd = dist(ox, oy, rx, ry)
        # Prefer resources we are closer to; if tie, prefer ones farther from opponent (more denial).
        key = (opd - myd, -abs(rx - (w - 1) / 2) - abs(ry - (h - 1) / 2), myd)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    if best_t is None:
        # No resources visible: drift toward center while maintaining distance from opponent.
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best_t

    moves = []
    # Deterministic move preference order: stay, then N,S,E,W, then diagonals
    for dx, dy in [(0,0),(0,-1),(0,1),(-1,0),(1,0),(-1,-1),(1,-1),(-1,1),(1,1)]:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Evaluate: reduce distance to target, keep away from opponent, and slightly bias diagonals toward center.
        before = dist(x, y, ox, oy)
        after = dist(nx, ny, ox, oy)
        d_t = dist(nx, ny, tx, ty)
        center_bias = -abs(nx - (w - 1) / 2) - abs(ny - (h - 1) / 2)
        denom = 1 if dx == 0 or dy == 0 else 0
        key = (d_t, -after, -center_bias, denom, dx, dy)
        moves.append((key, [dx, dy]))
    if moves:
        moves.sort(key=lambda z: z[0])
        return moves[0][1]

    return [0, 0]