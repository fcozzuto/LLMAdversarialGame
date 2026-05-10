def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    cand = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inside(rx, ry) or (0 <= rx < w and 0 <= ry < h):
                ds = man(sx, sy, rx, ry)
                do = man(ox, oy, rx, ry)
                # Prefer resources we can reach before/at opponent; then prefer larger advantage.
                cand.append((do - ds, -ds, rx, ry))
    if not cand:
        return [0, 0]

    cand.sort(reverse=True)
    tx, ty = cand[0][2], cand[0][3]

    # If opponent is closer to our target by a lot, switch to a resource that best blocks them.
    # (Deterministic "resource denial" rather than chasing single nearest.)
    if len(cand) > 1:
        best_adv = cand[0][0]
        sec_adv = cand[1][0]
        if best_adv < -2 and sec_adv > best_adv - 1:
            tx, ty = cand[1][2], cand[1][3]

    dx = 0
    dy = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    # Greedy move choice among the 9 options, avoiding obstacles; prefer moves that reduce distance to (tx,ty),
    # while also increasing opponent's distance to (tx,ty).
    options = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for mx, my in options:
        nx, ny = sx + mx, sy + my
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue
        self_d = man(nx, ny, tx, ty)
        opp_d = man(ox, oy, tx, ty)
        cur_self_d = man(sx, sy, tx, ty)
        # Score: primarily reduce our distance; secondarily increase opponent's ability relative to us (via our distance change).
        score = (-(self_d - cur_self_d), -(self_d), (self_d - opp_d))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]