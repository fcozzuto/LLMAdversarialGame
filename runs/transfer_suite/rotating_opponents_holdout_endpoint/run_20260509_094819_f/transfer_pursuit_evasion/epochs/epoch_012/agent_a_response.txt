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

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    self_ev = "evad" in self_role
    opp_ev = "evad" in opp_role

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def neighbors_count(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                c += 1
        return c

    def opp_choice(px, py):
        # choose opponent move that optimizes their objective against our predicted position (px,py)
        best = None
        best_val = None
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if not ok(nx, ny):
                continue
            if nx == px and ny == py:
                val = -10**9 if opp_ev else 10**9
            else:
                ddx, ddy = px - nx, py - ny
                d2 = ddx * ddx + ddy * ddy
                val = (d2 if opp_ev else -d2)
                val += neighbors_count(nx, ny) * (0.15 if opp_ev else 0.05)
            if best is None or (val > best_val):
                best, best_val = (nx, ny), val
        if best is None:
            return ox, oy
        return best[0], best[1]

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ax, ay = opp_choice(nx, ny)  # one-step lookahead
        if ax == nx and ay == ny:
            score = -10**12 if self_ev else 10**12
        else:
            ddx, ddy = nx - ax, ny - ay
            d2 = ddx * ddx + ddy * ddy
            score = (d2 if self_ev else -d2)
            score += neighbors_count(nx, ny) * (0.25 if self_ev else 0.10)

        if best_score is None or (score > best_score):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]