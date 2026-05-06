def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def manh(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    # Pick a resource where we are relatively closer than the opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        # Maximize (opponent advantage - our disadvantage): do - ds, tie-break by closer ds
        key = (do - ds, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    bestm = [0, 0]
    bestscore = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles:
            continue
        if nx < 0 or ny < 0 or nx >= observation["grid_width"] or ny >= observation["grid_height"]:
            continue
        ns = manh(nx, ny, tx, ty)
        no = manh(nx, ny, ox, oy)
        # Prefer getting closer to target, while not allowing opponent too much proximity
        score = (-(ns), -no, -dx, -dy)
        if bestscore is None or score > bestscore:
            bestscore = score
            bestm = [dx, dy]

    # If all legal moves were blocked, stay.
    return bestm