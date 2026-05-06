def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def d(a, b, c, e):
        return abs(a - c) + abs(b - e)

    opp_dist = d(sx, sy, ox, oy)
    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        nearest = 10**9
        nearest2 = 10**9
        for rx, ry in resources:
            dd = d(nx, ny, rx, ry)
            if dd < nearest:
                nearest2 = nearest
                nearest = dd
            elif dd < nearest2:
                nearest2 = dd

        new_opp = d(nx, ny, ox, oy)
        # Prefer immediate resource capture, then approach while keeping some separation from opponent,
        # and avoid moves that increase opponent reach to our current target.
        capture = 1 if (nx, ny) in resources else 0
        # Opponent pressure proxy: how much closer opponent gets to our nearest resource set.
        # Use only local info: distance reduction to the same "nearest" resource from opponent.
        target = None
        best_local = None
        for rx, ry in resources:
            dd = d(sx, sy, rx, ry)
            if best_local is None or dd < best_local or (dd == best_local and (rx, ry) < target):
                best_local = dd
                target = (rx, ry)
        if target is None:
            target = resources[0]
        tx, ty = target
        opp_to_target = d(ox, oy, tx, ty)
        opp_after = d(ox, oy, tx, ty)  # opponent position fixed this turn
        # so this term mainly uses opponent vs our progress, not opponent movement.

        key = (
            -capture,
            nearest,
            -new_opp if opp_dist >= 2 else -(new_opp + 1),
            -((d(nx, ny, tx, ty) - d(sx, sy, tx, ty))),
            dx == 0 and dy == 0,
            (nx, ny),
        )
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])] if best is not None else [0, 0]