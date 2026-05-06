def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is not None and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (-(10**9), 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            dcent = man(nx, ny, cx, cy)
            dob = man(nx, ny, ox, oy)
            # keep away from opponent while approaching center deterministically
            key = (-dcent + 0.02 * dob, -dob, nx, ny)
            if key > best:
                best = key
        return [best[2] - sx, best[3] - sy]

    # one-step lookahead: choose move that maximizes advantage on the best contested resource
    best_key = (-(10**18), 0, 0)
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        # small tie-break towards reducing distance to some promising resource
        best_adv = -(10**18)
        best_self_d = 10**9
        best_opp_d = 10**9
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            # reward resources we can reach no later than opponent; otherwise still punish when opponent is closer
            adv = (opp_d - self_d) - 0.05 * self_d
            if adv > best_adv or (adv == best_adv and (self_d < best_self_d or (self_d == best_self_d and (opp_d < best_opp_d)))):
                best_adv = adv
                best_self_d = self_d
                best_opp_d = opp_d

        # extra shaping: prefer moving slightly away from opponent if advantages tie
        dob = man(nx, ny, ox, oy)
        # deterministic final key: advantage first, then opponent distance, then remaining resource distance
        key = (best_adv, dob, -best_self_d, nx, ny)
        if key > best_key:
            best_key = key
            best_move = (nx - sx, ny - sy)

    return [int(best_move[0]), int(best_move[1])]