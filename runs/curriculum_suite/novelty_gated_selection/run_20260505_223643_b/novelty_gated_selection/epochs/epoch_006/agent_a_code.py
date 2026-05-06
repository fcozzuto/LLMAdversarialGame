def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Denial focus: resources that opponent is nearest to (likely contested).
    top = sorted(resources, key=lambda r: (cheb(ox, oy, r[0], r[1]), cheb(sx, sy, r[0], r[1])))
    focus = top[: min(4, len(top))]

    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Try to "win" a contested resource while also making opponent's situation worse.
        score = 0.0
        for rx, ry in focus:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Advantage now: how much closer we are than the opponent.
            adv = d_op - d_me
            # If we can get within 1 step advantage, heavily reward (denial).
            denial = 30.0 if adv >= 1 else (10.0 if adv >= 0 else -15.0)
            # Prefer finishing quickly for whichever contested resource we target.
            finish = -2.5 * d_me
            score += denial + finish

        # Small tie-break: prefer moves that reduce our nearest resource distance.
        nearest_now = min(cheb(nx, ny, r[0], r[1]) for r in resources)
        score += -0.15 * nearest_now

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]