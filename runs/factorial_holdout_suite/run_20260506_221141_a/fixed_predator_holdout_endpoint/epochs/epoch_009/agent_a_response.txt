def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    if not resources:
        return [0, 0]

    obst = {(int(a), int(b)) for a, b in obstacles}
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick a resource we can reach with clear relative advantage (opp closer => worse).
    best = None
    best_key = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        adv = od - sd  # larger means we are closer
        key = (-adv, sd, od, rx, ry)  # maximize adv; then smaller sd; then deterministic
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # Choose a legal step that maximizes our advantage on that target, with obstacle avoidance.
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue
        nsd = md(nx, ny, tx, ty)
        nod = md(ox, oy, tx, ty)  # opponent position unchanged this turn
        adv = nod - nsd
        # Prefer higher adv; then smaller nsd; then keep movement minimal; deterministic tie-break.
        key = (-adv, nsd, abs(dx) + abs(dy), dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]