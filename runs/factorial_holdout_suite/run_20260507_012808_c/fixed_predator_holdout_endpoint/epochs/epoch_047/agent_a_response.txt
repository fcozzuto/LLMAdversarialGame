def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    # 1-ply lookahead: pick the move that maximizes our ability to arrive before opponent,
    # with slight preference for nearer pickup.
    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # Evaluate move by best resource we can contest from new position.
        best_here_key = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            steal_margin = od - sd  # positive => we are closer
            # If we can reach sooner (or tie), strongly favor.
            # Add small tie-break to prefer cells closer to corners/center balance deterministically.
            reach_key = (steal_margin, -sd, -(abs(rx - (w // 2)) + abs(ry - (h // 2))), rx, ry)
            if best_here_key is None or reach_key > best_here_key:
                best_here_key = reach_key
        if best_key is None or best_here_key > best_key:
            best_key = best_here_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]