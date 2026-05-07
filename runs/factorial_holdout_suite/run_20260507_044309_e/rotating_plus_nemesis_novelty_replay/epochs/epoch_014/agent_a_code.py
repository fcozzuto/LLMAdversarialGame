def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (None, None)  # (score tuple, move)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        best_for_move = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # resource_denier: contest what opponent is closest to; advantage is od - sd
            adv = od - sd
            # If we can get it first, heavily prefer; else prefer reducing opponent gap.
            primary = adv
            # Secondary: prefer smaller our distance to win; also prefer targets opponent is already near.
            secondary = -sd
            tertiary = -od
            # Extra: if our move increases distance to all targets we could win, penalize via sd+od
            quaternary = -(sd + od)
            val = (primary, secondary, tertiary, quaternary)
            if best_for_move is None or val > best_for_move:
                best_for_move = val

        if best_for_move is None:
            continue
        if best[0] is None or best_for_move > best[0] or (best_for_move == best[0] and (dx, dy) < best[1]):
            best = (best_for_move, (dx, dy))

    if best[1] is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]