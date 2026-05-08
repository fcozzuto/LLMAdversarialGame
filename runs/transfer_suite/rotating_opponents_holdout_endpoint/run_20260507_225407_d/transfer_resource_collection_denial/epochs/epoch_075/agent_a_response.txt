def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                resources.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Target resource: prefer where we are relatively closer than opponent.
    best_t = resources[0]
    best_key = (10**9, 10**9, 10**9)
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        # Primary: minimize advantage gap (sd-od). Secondary: closer to us.
        # Tertiary: deterministic preference by coordinates.
        key = (sd - od, sd, rx * 100 + ry)
        # If opponent shares our row, bias toward that row to counter sweep patterns.
        if ry == oy:
            key = (key[0] - 2, key[1] - 1, key[2])
        if key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    # Choose move that reduces our distance to target; break ties by avoiding opponent closeness.
    best_m = legal[0]
    best_mv = (10**9, -10**9, 10**9)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        sd = md(nx, ny, tx, ty)
        od_next = md(ox, oy, tx, ty)
        # Move quality: smaller sd; then prefer making opponent not better (increase od_next relative not possible),
        # so use (od_next - sd) as tie-break; then deterministic coordinate of move.
        opp_gap = od_next - sd
        mv_key = (sd, -opp_gap, (dx + 1) * 10 + (dy + 1))
        if mv_key < best_mv:
            best_mv = mv_key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]