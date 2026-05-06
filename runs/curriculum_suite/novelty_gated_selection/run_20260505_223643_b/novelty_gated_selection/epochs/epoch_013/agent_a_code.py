def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Interfere with sweep-by-row: prioritize resources on opponent's current row.
    # If none, fall back to fastest-to-reach resource with mild "behind" pressure.
    best = None
    best_key = None
    for rx, ry in resources:
        dS = cheb(sx, sy, rx, ry)
        dO = cheb(ox, oy, rx, ry)
        on_row = 1 if ry == oy else 0
        # Key: maximize row-interference, then maximize our advantage margin, then bias to farther-from-opponent-x
        key = (
            on_row,
            dO - dS,
            (abs(ox - rx) * (1 if on_row else 0.5)),
            -((rx + 7 * ry) % 13),
        )
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    moves = [
        (dx, dy),
        (dx, 0),
        (0, dy),
        (dx, -dy),
        (-dx, dy),
        (-dx, 0),
        (0, -dy),
        (0, 0),
    ]

    # Obstacle-aware choose: prefer move that reduces distance while not stepping into obstacle.
    curd = cheb(sx, sy, tx, ty)
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        if nd <= curd:
            return [mx, my]

    # If all reducing/valid are blocked, take any safe move; otherwise stay.
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [mx, my]
    return [0, 0]