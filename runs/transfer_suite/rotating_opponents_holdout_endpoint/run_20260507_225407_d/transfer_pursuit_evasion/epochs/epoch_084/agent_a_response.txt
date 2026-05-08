def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles or not inb(x, y)

    def dist(x, y):
        return max(abs(x - ox), abs(y - oy))  # Chebyshev capture metric

    role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role)  # pursuer tries to minimize distance

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    # Target corner based on role: pursuer targets closest, evader targets farthest
    if is_pursuer:
        tx, ty = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    else:
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # compress to allowed dx/dy only (diagonal allowed already), but ensure each is in {-1,0,1}
    moves = [(dx, dy) for dx, dy in moves if dx in (-1, 0, 1) and dy in (-1, 0, 1)]

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        d = dist(nx, ny)
        # Corner pressure
        corner_d = abs(nx - tx) + abs(ny - ty)

        # Avoid stepping into cells that are "closer to opponent's target direction" for evader
        # Deterministic: compute opponent-biased direction
        opp_dir_x = 0 if ox == tx else (1 if tx > ox else -1)
        opp_dir_y = 0 if oy == ty else (1 if ty > oy else -1)
        align = (nx - ox) * opp_dir_x + (ny - oy) * opp_dir_y  # larger means aligned toward target from opponent

        if is_pursuer:
            # minimize capture distance; also prefer reducing corner_d (toward opponent-side corner)
            key = (-d, -corner_d, -align, 0 if dx == 0 else -1, 0 if dy == 0 else -1)
        else:
            # maximize survival distance; also prefer increasing corner_d (toward farthest corner)
            key = (d, -corner_d, -align, -dx * dx - dy * dy)

        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best