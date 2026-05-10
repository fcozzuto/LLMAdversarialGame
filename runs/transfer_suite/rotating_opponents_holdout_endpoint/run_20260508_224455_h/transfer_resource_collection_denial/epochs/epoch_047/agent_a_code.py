def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        adv = do - ds  # positive => we are closer
        # Prefer: we are closer/equal; then larger advantage; then smaller our distance; tie by coords
        key = (0 if adv >= 0 else 1, -adv, ds, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)

    tx, ty = best[1], best[2]
    best_move = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dself = dist(nx, ny, tx, ty)
        dopp = dist(ox, oy, tx, ty)
        # Prefer reducing distance to target; and if possible, keep/extend being closer than opponent
        target_adv = dself - dopp  # smaller is better
        # Tie-break: deterministic ordering by move list position
        key = (dself, target_adv, abs(dx), abs(dy), moves.index((dx, dy)))
        if best_move is None or key < best_move[0]:
            best_move = (key, dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[1], best_move[2]]