def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((r[0], r[1]))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if inside(nx, ny) else [0, 0]

    # Pick a target resource: prefer ones I'm closer to than the opponent.
    best_t = None
    best_key = None
    for rx, ry in resources:
        dm = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        key = (dm - do, dm, rx, ry)  # smaller dm-do => opponent closer; so we invert later by choosing max
        # We want maximize (do - dm) while tie-breaking by smaller dm.
        score_key = (-(dm - do), dm, rx, ry)
        if best_key is None or score_key < best_key:
            best_key = score_key
            best_t = (rx, ry)

    tx, ty = best_t

    # Evaluate each move: get closer to target, keep distance from opponent, avoid indecision.
    best_move = None
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        my_d = md(nx, ny, tx, ty)
        opp_d = md(nx, ny, ox, oy)
        # Prefer smallest my_d; then largest opp_d; then deterministic tie on move.
        val = (my_d, -opp_d, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]