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
    is_evader = ("evader" in role_s) or ("avoid" in role_s) or ("runner" in role_s) or ("flee" in role_s) or ("evade" in role_s)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def cheb(x, y):
        dx = abs(ox - x)
        dy = abs(oy - y)
        return dx if dx > dy else dy

    def mobility(x, y):
        m = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                m += 1
        return m

    def obstacle_penalty(x, y):
        # Prefer not to be adjacent to many obstacles/corners trapping.
        adj = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                adj += 1
        return adj

    # Deterministic tiebreak: iterate in fixed order, keep first best.
    best_move = [0, 0]
    if is_evader:
        best_val = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                nx, ny = sx, sy
            dist = cheb(nx, ny)
            mob = mobility(nx, ny)
            pen = obstacle_penalty(nx, ny)
            # Extra: if distance can't increase, still prefer safer (higher mobility, lower penalty).
            val = dist * 20 + mob * 2 - pen * 3
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
    else:
        best_val = 10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                nx, ny = sx, sy
            dist = cheb(nx, ny)
            mob = mobility(nx, ny)
            pen = obstacle_penalty(nx, ny)
            # Pursuer: minimize distance; also avoid getting stuck.
            val = dist * 20 - mob * 2 + pen * 3
            if val < best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]