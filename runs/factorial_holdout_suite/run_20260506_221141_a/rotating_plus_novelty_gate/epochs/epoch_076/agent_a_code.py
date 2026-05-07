def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = [m for m in moves if True]

    best_move = (0, 0)
    best_val = -10**18

    tr = int(observation.get("turns_remaining", 0) or 0)
    urgency = 1.0 + (0.35 if tr <= 8 else (0.2 if tr <= 16 else 0.0))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue

        val = 0.0
        my_d0 = dist((nx, ny), (ox, oy))  # used only for mild tie-break
        for rx, ry in resources:
            rd = dist((nx, ny), (rx, ry))
            od = dist((ox, oy), (rx, ry))
            # Prefer resources where we are closer than opponent; if not, still pick those minimizing "we-lag".
            lead = (od - rd)
            # Deterministic small preference: closer absolute distance slightly better as game tightens.
            tight = rd + (0.5 if tr <= 12 else 0.0)
            val += (100.0 * lead - 2.0 * tight) * urgency

        # If multiple lead similarly, steer away from opponent a bit to reduce denial risk.
        val -= 0.05 * my_d0

        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            # deterministic tie-break: prefer moves with smallest |dx|+|dy| then lexicographic
            cur = abs(best_move[0]) + abs(best_move[1])
            nxt = abs(dx) + abs(dy)
            if nxt < cur or (nxt == cur and (dx, dy) < best_move):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]