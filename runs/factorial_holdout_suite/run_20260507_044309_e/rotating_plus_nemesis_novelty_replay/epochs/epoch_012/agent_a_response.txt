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
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Choose move that maximizes our distance advantage for some reachable resource.
        # Score tuple is compared lexicographically after max via negation pattern.
        best_here = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # Primary: we want od - sd large (we're closer than opponent).
            # Secondary: prefer smaller sd to secure first.
            # Tertiary: prefer smaller absolute race gap to avoid indecision? (use od as stabilizer)
            cand = (od - sd, -sd, -od)
            if best_here is None or cand > best_here:
                best_here = cand

        if best_here is None:
            continue
        if best_val is None or best_here > best_val:
            best_val = best_here
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]