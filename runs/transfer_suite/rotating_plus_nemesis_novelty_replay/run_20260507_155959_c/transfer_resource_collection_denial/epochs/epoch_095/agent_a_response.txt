def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if dx == 0 and dy == 0:
                moves.append((0, 0))
            elif inb(nx, ny) and (nx, ny) not in obs:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        tx = w - 1 if ox < w // 2 else 0
        ty = h - 1 if oy < h // 2 else 0
        best = min(moves, key=lambda m: md(sx + m[0], sy + m[1], tx, ty))
        return [best[0], best[1]]

    # Choose moves by maximizing "we're closer than opponent" first, then nearest.
    # Deterministic tie-breaking by resource coordinates.
    rlist = [(int(x), int(y)) for (x, y) in resources]
    rlist.sort()

    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # Prefer resources where we have an advantage after this move.
        # Higher advantage is better; if equal, smaller own distance is better.
        best_for_move = None
        for rx, ry in rlist:
            d_me = md(nx, ny, rx, ry)
            d_op = md(ox, oy, rx, ry)
            adv = d_op - d_me  # >0 means we are closer/equal than opponent
            key = (adv, -d_me, -rx, -ry)  # deterministic: adv, then nearer (via -d_me), then by coords
            if best_for_move is None or key > best_for_move:
                best_for_move = key
        # Convert to overall key: maximize best_for_move lexicographically
        overall_key = best_for_move
        if best_key is None or overall_key > best_key:
            best_key = overall_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]