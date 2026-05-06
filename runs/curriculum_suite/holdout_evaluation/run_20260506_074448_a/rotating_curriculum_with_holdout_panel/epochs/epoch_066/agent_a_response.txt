def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    # Pick the resource opponent is currently closest to (most likely target for safe_collector).
    best_target = None
    best_opp_d = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        od = man(ox, oy, rx, ry)
        if best_target is None or od < best_opp_d or (od == best_opp_d and (rx, ry) < best_target):
            best_target = (rx, ry)
            best_opp_d = od
    if best_target is None:
        return [0, 0]
    tx, ty = best_target

    # Also consider next-best to avoid corner cases where closest target is blocked by movement.
    other_targets = []
    for rx, ry in resources:
        if (rx, ry) in obstacles or (rx, ry) == best_target:
            continue
        other_targets.append((man(ox, oy, rx, ry), rx, ry))
    other_targets.sort()

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_d = man(nx, ny, tx, ty)
        opp_d = best_opp_d

        # Core: race the opponent on their likely target.
        # Maximize (opp_d - my_d) => we want our distance to be smaller.
        score = (opp_d - my_d) * 10.0

        # Secondary: if we can't beat them, at least shrink our distance to their target
        # and slightly move toward center to keep mobility.
        score += -(my_d) * 1.5

        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        ddx = nx - cx
        ddy = ny - cy
        score += -(ddx * ddx + ddy * ddy) * 0.002

        # Tertiary: if we are much closer to some other resource that opponent is also contesting,
        # prefer moves that potentially switch contest lines.
        if other_targets:
            top2 = other_targets[:2]
            for od2, rx2, ry2 in top2:
                my2 = man(nx, ny, rx2, ry2)
                score += (od2 - my2) * 2.0

        # Strong immediate capture preference if moving onto a resource.
        if (nx, ny) in resources:
            score += 1000.0

        if score > best_score or (score == best_score and (dx, dy) < tuple(best_move)):
            best_score = score
            best_move = [dx, dy]

    return best_move