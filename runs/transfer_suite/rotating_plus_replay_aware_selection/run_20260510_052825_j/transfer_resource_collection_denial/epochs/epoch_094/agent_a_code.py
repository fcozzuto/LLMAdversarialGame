def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best_res = None
    best_key = None
    for rx, ry in resources:
        if not legal(rx, ry):
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can get earlier than opponent.
        key = (od - sd, sd, od, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    if best_res is None:
        # fallback: ignore legality for target selection
        rx, ry = min(resources, key=lambda p: (cheb(ox, oy, p[0], p[1]) - cheb(sx, sy, p[0], p[1]), cheb(sx, sy, p[0], p[1]), p[0], p[1]))
        best_res = (rx, ry)

    tx, ty = best_res

    # Choose move that maximizes (opponent_lead - our_distance) with small tie-break toward target.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            nx, ny = sx, sy
        our_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # Higher score is better.
        score = (opp_d - our_d, -our_d, -cheb(nx, ny, ox, oy), -abs((tx - nx)) - abs((ty - ny)), tx, ty)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]