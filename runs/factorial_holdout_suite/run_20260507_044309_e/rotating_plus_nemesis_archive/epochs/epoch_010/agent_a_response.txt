def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = -dist((nx, ny), (cx, cy))
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best_move = [0, 0]
    best_val = -10**18

    # Race: pick a resource where we can beat the opponent soonest.
    for rx, ry in resources:
        cur_self = dist((sx, sy), (rx, ry))
        cur_opp = dist((ox, oy), (rx, ry))
        # If opponent is closer, still choose it if we can close the gap quickly.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            ns = dist((nx, ny), (rx, ry))
            no = cur_opp  # opponent position unchanged this turn
            advantage = (no - ns)
            # Finish quickly + prevent handing resources where opponent keeps advantage.
            val = advantage * 1000 - ns
            # Mild "denial response": prefer moves that also increase distance from opponent
            val += (dist((nx, ny), (ox, oy)) - dist((sx, sy), (ox, oy))) * 3
            # If we're making progress toward a currently contested resource, boost.
            if ns < cur_self:
                val += 50
            if val > best_val:
                best_val = val
                best_move = [dx, dy]

    return best_move