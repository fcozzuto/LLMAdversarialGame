def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def is_evader(role):
        r = (role or "").lower()
        return ("evader" in r) or ("runner" in r) or ("evasion" in r) or ("evasive" in r)

    self_evader = is_evader(observation.get("self_role"))
    opp_evader = is_evader(observation.get("opponent_role"))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def score_pos(ax, ay, bx, by, for_evader):
        d = man(ax, ay, bx, by)
        # Capture at radius 0: if positions match
        if d == 0:
            return -10**9 if not for_evader else 10**9
        return d if for_evader else -d  # evader wants larger d, pursuer wants smaller d

    def pick_opponent_move(px, py, ourx, oury):
        best = None
        best_sc = None
        for ddx, ddy in dirs:
            nx, ny = px + ddx, py + ddy
            if not valid(nx, ny):
                continue
            sc = score_pos(nx, ny, ourx, oury, opp_evader)
            if best_sc is None or sc > best_sc:
                best_sc = sc
                best = (ddx, ddy)
        return best if best is not None else (0, 0)

    best_move = (0, 0)
    best_out = None
    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not valid(nx, ny):
            continue
        # Greedy opponent response based on our new position
        odx, ody = pick_opponent_move(ox, oy, nx, ny)
        nx2, ny2 = ox + odx, oy + ody
        if self_evader:
            # we want opponent far from us after their move
            out = man(nx, ny, nx2, ny2)
        else:
            # we want us to be close to opponent after their move
            out = -man(nx, ny, nx2, ny2)
            if nx == nx2 and ny == ny2:
                out += 10**8
        if best_out is None or out > best_out:
            best_out = out
            best_move = (ddx, ddy)

    return [int(best_move[0]), int(best_move[1])]