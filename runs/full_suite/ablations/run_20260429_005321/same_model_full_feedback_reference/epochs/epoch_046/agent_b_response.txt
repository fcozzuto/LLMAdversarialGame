def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    # Alternate targeting rule to change behavior if prior epoch underperformed
    even_turn = (int(observation.get("turn_index") or 0) % 2 == 0)

    if resources:
        best = None
        best_key = None
        for tx, ty in sorted(resources):
            ds = d2(sx, sy, tx, ty)
            do = d2(ox, oy, tx, ty)
            if even_turn:
                # maximize how much closer we are than opponent (advantage first, then closer)
                key = (do - ds, -ds, -abs(tx - (w - 1)), -abs(ty - (h - 1)), tx, ty)
            else:
                # minimize our distance, but penalize targets opponent is too close to
                key = (-ds, do - ds, abs(tx - (w - 1)), abs(ty - (h - 1)), tx, ty)
            if best_key is None or key > best_key:
                best_key = key
                best = (tx, ty)
        tx, ty = best
    else:
        # No visible resources: move toward opponent's corner to reduce race tempo
        tx, ty = (w - 1, h - 1)

    # Choose move that reduces distance to target; add mild repulsion from obstacles by discouraging staying adjacent isn't needed (obstacles handled by ok)
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ds = d2(nx, ny, tx, ty)
        # Avoid letting opponent get closer to our chosen target while we drift
        do_next = d2(ox, oy, tx, ty)
        val = (-ds, -(do_next - ds), abs(nx - ox) + abs(ny - oy), nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]