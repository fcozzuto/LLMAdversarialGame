def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def manh(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_key = None
    for tx, ty in resources:
        ds = manh(sx, sy, tx, ty)
        do = manh(ox, oy, tx, ty)
        adv = do - ds  # positive => we're closer
        # Prefer resources where we can beat opponent; then close ourselves.
        if best_key is None or (adv > best_key[0]) or (adv == best_key[0] and (ds < best_key[1] or (ds == best_key[1] and (tx, ty) < best_key[2]))):
            best_key = (adv, ds, (tx, ty))
            best = (tx, ty)

    tx, ty = best

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        ds_next = manh(nx, ny, tx, ty)

        # If stepping can contest a nearby resource better than opponent, weight it slightly.
        contest = 0
        for rx, ry in resources:
            if abs(rx - tx) + abs(ry - ty) <= 2:
                dsn = manh(nx, ny, rx, ry)
                don = manh(ox, oy, rx, ry)
                if don - dsn > 0:
                    contest += 1

        val = ds_next - 0.35 * contest
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    # If all moves blocked (unlikely), stay.
    return [int(best_move[0]), int(best_move[1])]