def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for it in observation.get("obstacles") or []:
        if isinstance(it, (list, tuple)) and len(it) >= 2:
            x, y = int(it[0]), int(it[1])
            if 0 <= x < gw and 0 <= y < gh:
                obstacles.add((x, y))

    resources = []
    for it in observation.get("resources") or []:
        if isinstance(it, (list, tuple)) and len(it) >= 2:
            x, y = int(it[0]), int(it[1])
            if 0 <= x < gw and 0 <= y < gh and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    best = None
    best_key = None
    for rx, ry in resources:
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        # Prefer resources where we are ahead; otherwise, choose the one that limits their access.
        # Tie-break: closer, then deterministic ordering.
        ahead = do - ds  # positive means we are closer
        contested = max(ds, do)
        key = (-ahead, contested, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best

    # Move one step toward target, avoiding obstacles if possible.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    # If all diagonal/adjacent blocked, allow staying.
    if not moves:
        return [0, 0]

    # Deterministic preference ordering by resulting distance, then dx/dy.
    def move_key(m):
        dx, dy = m
        nx, ny = sx + dx, sy + dy
        d = manh(nx, ny, rx, ry)
        return (d, abs(dx), abs(dy), dx, dy)

    best_move = min(moves, key=move_key)

    # Occasionally consider staying if staying keeps us from stepping into a trap:
    # If all moves worsen our relative position to the opponent by the same amount, keep still deterministically.
    nx, ny = sx + best_move[0], sy + best_move[1]
    rel_before = manh(sx, sy, rx, ry) - manh(ox, oy, rx, ry)
    rel_after = manh(nx, ny, rx, ry) - manh(ox, oy, rx, ry)
    if rel_after > rel_before:
        return [0, 0]
    return [best_move[0], best_move[1]]