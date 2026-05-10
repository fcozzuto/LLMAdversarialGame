def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            blocked.add((int(o[0]), int(o[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    role = (observation.get("self_role", "") or "").lower()
    env = (observation.get("environment_name", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("evasion" in role) or ("escape" in role) or ("evasion" in env) or ("escape" in env)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            if inb(x + dx, y + dy):
                c += 1
        return c

    def opp_moves(px, py):
        res = []
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if inb(nx, ny):
                res.append((nx, ny))
        if not res:
            return [(px, py)]
        return res

    self_is_pursuer = not is_evader
    best_move = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy

        my_mob = mobility(nx, ny)
        if self_is_pursuer:
            # worst-case: opponent (evader) maximizes distance from our new position
            worst = -1
            for ex, ey in opp_moves(ox, oy):
                d = cheb(nx, ny, ex, ey)
                if d > worst:
                    worst = d
            val = -(worst * 20 + (7 - my_mob) * 3)
        else:
            # worst-case: opponent pursuer minimizes our distance next step
            best = 10**9
            for px, py in opp_moves(ox, oy):
                d = cheb(px, py, nx, ny)
                if d < best:
                    best = d
            val = best * 20 + my_mob * 2

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]