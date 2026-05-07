def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # Choose move by contesting the resource where we can arrive no later than opponent,
    # preferring smallest arrival time if contested, else best spread (opp-self).
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        best_for_move = None
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)

            # Prefer resources we can beat (od - sd large), but if we can tie/beat,
            # strongly prefer the one with smallest sd to secure first.
            if sd <= od:
                key = (1, sd, -od, rx, ry)  # primary: beat/tie, then fastest sd
            else:
                key = (0, -(od - sd), sd, rx, ry)  # primary: maximize advantage, then closer
            if best_for_move is None or key < best_for_move:
                best_for_move = key

        if best_for_move is None:
            continue

        # Global tie-break: choose move that gives best contested outcome; then reduce our sd.
        if best_key is None or best_for_move < best_key:
            best_key = best_for_move
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]