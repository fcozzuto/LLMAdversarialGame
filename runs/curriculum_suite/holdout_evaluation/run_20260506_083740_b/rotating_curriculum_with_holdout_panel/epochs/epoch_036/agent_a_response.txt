def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    tx0, ty0 = w // 2, h // 2
    if not resources:
        cx = 0 if sx == tx0 else (1 if sx < tx0 else -1)
        cy = 0 if sy == ty0 else (1 if sy < ty0 else -1)
        if valid(sx + cx, sy + cy):
            return [cx, cy]
        if valid(sx + cx, sy):
            return [cx, 0]
        if valid(sx, sy + cy):
            return [0, cy]
        return [0, 0]

    # Pick resource where we have the largest distance advantage, tie-break toward center.
    best_r = None
    best_a = None
    for r in resources:
        if not r or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        self_d = md(sx, sy, rx, ry)
        opp_d = md(ox, oy, rx, ry)
        adv = opp_d - self_d  # higher is better
        cen = md(rx, ry, tx0, ty0)
        key = (adv, -cen)
        if best_a is None or key > best_a:
            best_a = key
            best_r = (rx, ry)

    rx, ry = best_r if best_r is not None else (tx0, ty0)

    best_move = (0, 0)
    best_score = None
    # Evaluate each move by resulting advantage; add mild center bias for stability.
    for dx, dy in moves:
        nx, ny = int(sx + dx), int(sy + dy)
        if not valid(nx, ny):
            continue
        myd = md(nx, ny, rx, ry)
        oppd = md(ox, oy, rx, ry)
        adv = oppd - myd
        cen_bias = -md(nx, ny, tx0, ty0) * 0.01
        score = adv + cen_bias
        # tie-break deterministic: prefer smaller move (closer to current) then lexical by dx,dy order
        move_mag = abs(dx) + abs(dy) * 0.001
        score2 = score - move_mag
        if best_score is None or score2 > best_score:
            best_score = score2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]