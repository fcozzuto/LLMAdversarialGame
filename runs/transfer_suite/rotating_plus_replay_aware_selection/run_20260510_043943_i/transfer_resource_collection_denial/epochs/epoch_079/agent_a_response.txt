def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0),  (0, 0),  (1, 0),
              (-1, 1),  (0, 1),  (1, 1)]

    best_score = None
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            nx, ny = sx, sy
        if nx == sx and ny == sy and (dx, dy) != (0, 0):
            continue

        move_best = None
        # Resource selection for this hypothetical move
        for rx, ry in resources:
            if not cell_ok(rx, ry):
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)

            # Prefer resources where we can arrive sooner; penalize ones opponent can beat us to.
            # Also lightly prefer closer resources for tie-break consistency.
            # sweep_rows-ish: avoid resources that are in same row/col where opponent can race in.
            rowcol_race = (1 if (rx == ox or ry == oy) else 0)
            score = (sd - 0.85 * od + 0.35 * rowcol_race, sd, -((rx + ry) % 3))

            if move_best is None or score < move_best:
                move_best = score

        if move_best is None:
            continue

        if best_score is None or move_best < best_score:
            best_score = move_best
            best_move = [nx - sx, ny - sy]

    return [best_move[0], best_move[1]]