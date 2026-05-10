def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turns_remaining = observation.get("turns_remaining", 0)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    late = 1.0 if turns_remaining <= 10 else 0.0
    early = 1.0 - late

    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if dx == 0 and dy == 0:
            stay = 1
        else:
            stay = 0

        my_best = -10**18
        for rx, ry in resources:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if md == 0:
                rscore = 1000000.0
            else:
                win_margin = od - md
                rscore = win_margin * (22.0 + 18.0 * late) - md * (2.0 + 3.0 * early)
            # Slight bias to avoid giving up resources when already close
            if md <= 2:
                rscore += 6.0 * late
            if rscore > my_best:
                my_best = rscore

        # Encourage movement when early and we aren't improving access
        reg = 0.0
        if stay and early > 0:
            reg = -3.0
        if early > 0:
            reg += -cheb(nx, ny, ox, oy) * 0.2  # keep a bit of distance advantage

        total = my_best + reg
        if total > best[0]:
            best = (total, dx, dy)

    return [best[1], best[2]]