def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    self_role = observation.get("self_role", "pursuer")

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist2(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    def step_positions(x, y):
        out = []
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                out.append((nx, ny))
        if not out:
            out = [(x, y)]
        return out

    def min_obst_d2(x, y):
        md = 10**9
        for bx, by in obst:
            d = dist2(x, y, bx, by)
            if d < md:
                md = d
                if md == 0:
                    return 0
        return md if md != 10**9 else 999999

    my_steps = step_positions(sx, sy)

    # predict opponent as maximizing distance if we are pursuer; minimizing if we are evader
    opp_moves = step_positions(ox, oy)

    best = None
    best_val = None
    for nx, ny in my_steps:
        d_now = dist2(nx, ny, ox, oy)
        if d_now == 0:
            val = 10**12 if self_role == "pursuer" else -10**12
        else:
            if self_role == "pursuer":
                # opponent (evader) tries to maximize distance from our landing
                best_opp_d = -1
                for px2, py2 in opp_moves:
                    if dist2(px2, py2, nx, ny) > best_opp_d:
                        best_opp_d = dist2(px2, py2, nx, ny)
                val = -best_opp_d
                # also keep some obstacle clearance to handle wall-running
                val -= 0.01 * (1 + min_obst_d2(nx, ny))
            else:
                # opponent (pursuer) tries to minimize distance to us
                best_opp_d = 10**18
                for px2, py2 in opp_moves:
                    d = dist2(px2, py2, nx, ny)
                    if d < best_opp_d:
                        best_opp_d = d
                val = best_opp_d
                # for evader, stay away from obstacles too
                val -= 0.01 * (1 + (64 - min_obst_d2(nx, ny)))
        if best_val is None or (self_role == "pursuer" and val > best_val) or (self_role != "pursuer" and val > best_val):
            best_val = val
            best = (nx, ny)

    bx, by = best
    return [bx - sx, by - sy]