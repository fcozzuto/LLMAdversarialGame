def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    env = str(observation.get("environment_name", "")).lower()
    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()

    is_pursuer = ("pursu" in sr) or ("hunter" in sr)
    if "evasion" in env and (("evad" in sr) or ("escape" in sr) or ("runner" in sr)):
        is_pursuer = False
    if ("pursu" in orr) or ("hunter" in orr):
        is_pursuer = False
    if ("evad" in orr) or ("escape" in orr) or ("runner" in orr):
        is_pursuer = True

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
    far_corner = max(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_opp = cheb(nx, ny, ox, oy)
        if is_pursuer:
            primary = -d_to_opp
            secondary = -((abs(nx - ox) + abs(ny - oy)))
            val = (primary, secondary)
        else:
            d_to_corner = cheb(nx, ny, far_corner[0], far_corner[1])
            val = (d_to_opp, d_to_corner)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    # If all moves blocked (should be rare), stay put (engine keeps in place anyway)
    return [int(best_move[0]), int(best_move[1])]