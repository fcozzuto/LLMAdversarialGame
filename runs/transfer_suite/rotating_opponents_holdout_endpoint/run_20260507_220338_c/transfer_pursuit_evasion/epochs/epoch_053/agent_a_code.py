def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role_s = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role_s) or any(k in role_s for k in ("avoid", "runner", "flee"))

    deltas = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x, y):
        dx = abs(ox - x)
        dy = abs(oy - y)
        return dx if dx > dy else dy

    def man(x, y):
        return abs(ox - x) + abs(oy - y)

    def corner_bias(x, y):
        # Prefer corners for evader (common archetype), avoid for pursuer.
        d0 = (x - 0) ** 2 + (y - 0) ** 2
        d1 = (x - (w - 1)) ** 2 + (y - 0) ** 2
        d2 = (x - 0) ** 2 + (y - (h - 1)) ** 2
        d3 = (x - (w - 1)) ** 2 + (y - (h - 1)) ** 2
        return min(d0, d1, d2, d3)

    best_move = [0, 0]
    if is_evader:
        best_key = None  # maximize cheb, then maximize man, then minimize obstacle danger (via corner_bias)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                continue
            key = (cheb(nx, ny), man(nx, ny), -corner_bias(nx, ny))
            if best_key is None or key > best_key:
                best_key = key
                best_move = [dx, dy]
    else:
        # pursuer: reduce distance to exact capture; include obstacle-safe greedy.
        best_key = None  # minimize cheb, then minimize man, then prefer moving toward opponent's direction
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                continue
            toward_x = 1 if nx > sx else (-1 if nx < sx else 0)
            toward_y = 1 if ny > sy else (-1 if ny < sy else 0)
            dir_match = (0 if (ox == sx) else (-1 if (ox - sx) * toward_x < 0 else 1)) + (0 if (oy == sy) else (-1 if (oy - sy) * toward_y < 0 else 1))
            key = (cheb(nx, ny), man(nx, ny), -dir_match)
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]

    # Fallback if all candidate moves invalid
    if not (inb(sx + best_move[0], sy + best_move[1]) and (sx + best_move[0], sy + best_move[1]) not in blocked):
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]