def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Target resources where we are likely to arrive earlier; break ties by desirability (fewer self steps).
    best = None
    best_key = None
    for tx, ty in resources:
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        adv = od - sd  # positive means we are closer
        # slight center bias to avoid corner traps in early turns
        cb = abs(tx - (w - 1) / 2.0) + abs(ty - (h - 1) / 2.0)
        # Prefer big advantage; then shorter self distance; then lower center bias; then deterministic coord.
        key = (-(adv), sd, cb, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Try the direct move; if blocked, try axis moves in a deterministic order; else stay.
    moves = []
    moves.append((dx, dy))
    if dx != 0:
        moves.append((dx, 0))
    if dy != 0:
        moves.append((0, dy))
    # Deterministic fallback: try remaining combinations towards target.
    if dx != 0 and dy != 0:
        moves.append((dx, 0))
        moves.append((0, dy))

    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(mdx), int(mdy)]

    return [0, 0]