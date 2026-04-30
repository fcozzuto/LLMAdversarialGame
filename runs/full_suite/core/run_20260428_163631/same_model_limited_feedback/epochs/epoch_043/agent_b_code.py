def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    ox2 = sx + (ox - sx)
    target = None
    if resources:
        best = None
        for rx, ry in resources:
            myd = md(sx, sy, rx, ry)
            oppd = md(ox, oy, rx, ry)
            # Prefer resources we are closer to; tie-break by closer overall
            key = (myd - oppd, myd + oppd, myd)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        target = best[1]
    else:
        # No resources: head toward center-ish while keeping away from obstacles if possible
        target = (3.5, 3.5)

    tx, ty = target
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles:
            continue
        # distance to target (use continuous center if needed)
        dist_to_target = abs(nx - tx) + abs(ny - ty)
        # blocking: if opponent is adjacent, prefer moves that increase their distance
        dist_opp = md(nx, ny, ox, oy)
        # prefer moving onto resources
        on_resource = 1 if resources and (nx, ny) in set(tuple(p) for p in resources) else 0
        # primary: minimize my distance to target, then maximize separation from opponent
        score = (on_resource, -dist_to_target, dist_opp, -md(nx, ny, ox, oy), -md(nx, ny, tx if isinstance(tx, int) else 4, ty if isinstance(ty, int) else 4))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]