def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if resources:
        best = None
        for p in resources:
            rx, ry = p[0], p[1]
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive means we arrive sooner
            # Prefer decisive advantage; then smaller self distance; then deterministic position
            key = (-adv, sd, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        _, tx, ty = best

        # Choose best 1-step move that keeps heading to target and avoids letting opponent gain.
        best_move = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            nd = man(nx, ny, tx, ty)
            # Approximate "race": smaller distance helps, and we add a slight penalty
            # if opponent is very close to the target compared to us after this move.
            sd2 = nd
            od = man(ox, oy, tx, ty)
            est_adv = od - sd2
            key = (-est_adv, sd2, abs(nx - tx) + abs(ny - ty), nx, ny)
            if best_move is None or key < best_move[0]:
                best_move = (key, dx, dy)

        if best_move is not None:
            return [best_move[1], best_move[2]]

        return [0, 0]

    # No resources: move to a corner that we are closer to than the opponent.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best_corner = None
    for cx, cy in corners:
        sd = man(sx, sy, cx, cy)
        od = man(ox, oy, cx, cy)
        # Prefer corners we can reach earlier; then deterministic by coordinates
        key = (-(od - sd), sd, cx, cy)
        if best_corner is None or key < best_corner[0]:
            best_corner = (key, cx, cy)
    _, tx, ty = best_corner

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            # Greedy toward chosen corner with deterministic tie-break
            if man(nx, ny, tx, ty) < man(sx, sy, tx, ty) or (dx, dy) == (0, 0):
                return [dx, dy]

    return [0, 0]