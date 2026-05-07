def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in blocked:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    # If no resources, head toward opponent corner deterministically (bottom-right if start is top-left-like).
    if not resources:
        tx = w - 1 if sx < w - 1 else 0
        ty = h - 1 if sy < h - 1 else 0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Build a deterministic ordered list of candidate resources (sorted for stability).
    cand = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and in_bounds(x, y) and (x, y) not in blocked:
                cand.append((x, y))
    if not cand:
        return [0, 0]
    cand.sort(key=lambda p: (p[0], p[1]))

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        my_d_to = []
        for tx, ty in cand:
            myd = manh(nx, ny, tx, ty)
            oppd = manh(ox, oy, tx, ty)
            # Reward getting to a resource earlier; penalize resources opponent can beat.
            # Also slightly prefer smaller myd to finish faster.
            win = 1000 if myd < oppd else (250 if myd == oppd else -500)
            val = win - 3 * myd + 1 * oppd
            my_d_to.append(val)
        # Use max over resources: choose a move that improves the best "race outcome".
        score = max(my_d_to)
        # Tie-break: prefer moves that reduce distance to the best resource currently by sorted order.
        if score > best_val:
            best_val = score
            best_move = (dx, dy)
        elif score == best_val:
            # Deterministic secondary: smaller distance to the closest resource from new pos.
            td = min(manh(nx, ny, tx, ty) for tx, ty in cand)
            bd = min(manh(sx + best_move[0], sy + best_move[1], tx, ty) for tx, ty in cand)
            if td < bd:
                best_move = (dx, dy)
            elif td == bd:
                if (dx, dy) < best_move:
                    best_move = (dx, dy)

    return [best_move[0], best_move[1]]