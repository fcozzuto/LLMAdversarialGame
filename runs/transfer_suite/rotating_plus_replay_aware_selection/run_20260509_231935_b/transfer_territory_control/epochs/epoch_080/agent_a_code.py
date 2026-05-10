def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    targets = []
    unclaimed = observation.get("unclaimed_cells") or []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y) and (x, y) not in obs:
                targets.append((x, y))

    if not targets:
        targets = [(ox, oy)]

    move_options = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    # Choose nearest target by Manhattan; tie-break deterministically by coordinates.
    tx, ty = None, None
    best = None
    for x, y in targets:
        d = man(sx, sy, x, y)
        key = (d, x, y)
        if best is None or key < best:
            best = key
            tx, ty = x, y

    best_move = move_options[0]
    best_key = None
    for dx, dy in move_options:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        d_self = man(nx, ny, tx, ty)
        d_opp = man(nx, ny, ox, oy)
        key = (d_self, -d_opp, dx, dy)  # prefer closer target, also keep away from opponent
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move