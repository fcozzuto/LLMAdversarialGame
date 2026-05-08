def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                resources.append((x, y))
    if not resources:
        return [0, 0]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    def king_dist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    any_win = False
    for x, y in resources:
        if (x, y) in obstacles:
            continue
        our_t = king_dist(sx, sy, x, y)
        opp_t = king_dist(ox, oy, x, y)
        win_flag = our_t < opp_t
        if win_flag:
            any_win = True
        # Primary: win_flag. Secondary: maximize (opp_t - our_t). Tertiary: minimize our_t.
        key = (0 if win_flag else 1, -(opp_t - our_t), our_t, x, y)
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)

    # If tie for close competition, prefer moving toward a resource that keeps us closest next turn.
    tx, ty = best
    if (tx, ty) == (sx, sy):
        return [0, 0]

    dx = 0
    dy = 0
    if tx > sx: dx = 1
    elif tx < sx: dx = -1
    if ty > sy: dy = 1
    elif ty < sy: dy = -1

    # Avoid stepping into an obstacle if possible; try axis fallback deterministically.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles and dx != 0 and dy != 0:
        nx1, ny1 = sx + dx, sy
        if (nx1, ny1) not in obstacles:
            dx, dy = dx, 0
        else:
            nx2, ny2 = sx, sy + dy
            if (nx2, ny2) not in obstacles:
                dx, dy = 0, dy
            else:
                # last resort: stay
                dx, dy = 0, 0
    elif (nx, ny) in obstacles:
        # try moving along the other axis if diagonal blocked
        if dx != 0:
            nx2, ny2 = sx, sy + dy
        else:
            nx2, ny2 = sx + dx, sy
        if inb(nx2, ny2) and (nx2, ny2) not in obstacles:
            dx = nx2 - sx
            dy = ny2 - sy
        else:
            dx, dy = 0, 0

    if dx not in (-1, 0, 1): dx = 0
    if dy not in (-1, 0, 1): dy = 0
    return [dx, dy]