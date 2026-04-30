def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    tx, ty = sx, sy
    if resources:
        # Score resources: prefer ones we are closer to; if none, take a resource they contest but we can still fight for.
        best = None
        best_key = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Big bonus if we are strictly closer; otherwise modest pursuit if tie/slower.
            closer_bonus = 20 if sd < od else (8 if sd == od else 0)
            # Small penalty for longer time; deterministic tie-break by coordinate.
            key = (closer_bonus + (od - sd) * 2, -sd, -(rx * 9 + ry))
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    # Optionally nudge towards blocking contested targets: if opponent is closer to some resource, bias tx slightly towards it.
    if resources:
        contested = None
        best_key = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if od < sd:  # opponent closer
                key = (-(od - sd), -(rx * 9 + ry))
                if best_key is None or key > best_key:
                    best_key = key
                    contested = (rx, ry)
        if contested is not None:
            crx, cry = contested
            # If we are not too far, switch target to contest; else keep current.
            if cheb(sx, sy, crx, cry) <= 3:
                tx, ty = crx, cry

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        d_to_opp = cheb(nx, ny, ox, oy)
        # Prefer getting closer to target; avoid giving opponent immediate advantage by not moving into their vicinity.
        # Also prefer moves that approach resources directly if standing next to them.
        val = (-d_to_target * 10 + d_to_opp)
        # Deterministic tie-break: prefer diagonal, then right, then down, then staying.
        tie = (0 if dx != 0 and dy != 0 else 1, 0 if dx == 1 else (1 if dx == 0 else 2), 0 if dy == 1 else (1 if dy == 0 else 2), 0 if (dx, dy) == (0, 0) else 1)
        key = (val, -cheb(ox, oy, tx, ty), tie)
        if best_val is None or key > best_val:
            best_val = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]