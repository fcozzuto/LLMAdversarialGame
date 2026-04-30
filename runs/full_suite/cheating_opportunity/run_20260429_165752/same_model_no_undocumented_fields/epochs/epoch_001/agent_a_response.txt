def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    if resources:
        tx, ty = min(resources, key=lambda r: (abs(r[0] - x) + abs(r[1] - y), abs(r[0] - ox) + abs(r[1] - oy)))
    else:
        # No visible resources: advance to center to reduce distance to future spawns
        tx, ty = (w // 2, h // 2)

    dx = 0
    dy = 0
    if tx > x:
        dx = 1
    elif tx < x:
        dx = -1
    if ty > y:
        dy = 1
    elif ty < y:
        dy = -1

    moves = []
    # Primary: direct toward target (including diagonal)
    moves.append((dx, dy))
    # Secondary: try axis-aligned alternatives
    if dx != 0:
        moves.append((dx, 0))
    if dy != 0:
        moves.append((0, dy))
    # Tertiary: other neighbor moves in deterministic order
    for ddx in (-1, 0, 1):
        for ddy in (-1, 0, 1):
            if ddx == 0 and ddy == 0:
                continue
            if (ddx, ddy) not in moves:
                moves.append((ddx, ddy))
    if (0, 0) not in moves:
        moves.append((0, 0))

    best = None
    best_key = None
    for mdx, mdy in moves:
        nx, ny = x + mdx, y + mdy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Prefer moving closer to target; if tie, prefer farther from opponent (avoid immediate contest)
        key = (abs(tx - nx) + abs(ty - ny), -(abs(ox - nx) + abs(oy - ny)))
        if best_key is None or key < best_key:
            best_key = key
            best = (mdx, mdy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]