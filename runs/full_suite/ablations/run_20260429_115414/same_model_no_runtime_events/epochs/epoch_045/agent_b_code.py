def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    try:
        rem = int(observation.get("remaining_resource_count", 0) or 0)
    except:
        rem = 0
    late = rem <= 3

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev for 8-direction movement

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose a resource to "outpace" opponent on.
    target = None
    best_val = None
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        # Prefer resources opponent can't reach quickly; slight bias to closer ones.
        val = ds - 0.85 * do + (0.02 * (rx + ry))
        if best_val is None or val < best_val:
            best_val = val
            target = (rx, ry)

    # If no resources visible, or opponent dominates nearby, chase opponent deterministically.
    chase = False
    if late or target is None:
        chase = True
    elif resources:
        rx, ry = target
        if dist(ox, oy, rx, ry) + 1 <= dist(sx, sy, rx, ry):
            chase = True

    best_move = (0, 0)
    best_sc = None
    # Tie-break deterministically by fixed move order (already in list).
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if chase and resources:
            # Move to reduce distance to opponent while not blundering into obstacles already handled.
            sc = dist(nx, ny, ox, oy) + 0.01 * (nx + ny)
            # In chase mode, staying is worse unless it is best by distance.
            if dx == 0 and dy == 0:
                sc += 0.05
        else:
            if target is None:
                sc = dist(nx, ny, ox, oy)
            else:
                rx, ry = target
                ds2 = dist(nx, ny, rx, ry)
                do2 = dist(ox, oy, rx, ry)
                # Prefer progress toward target and slight safety from opponent gaining advantage.
                sc = ds2 - 0.7 * do2 + 0.02 * (nx + ny)
        if best_sc is None or sc < best_sc:
            best_sc = sc
            best_move = (dx, dy)

    # If all moves invalid (shouldn't happen), stay.
    return [int(best_move[0]), int(best_move[1])]