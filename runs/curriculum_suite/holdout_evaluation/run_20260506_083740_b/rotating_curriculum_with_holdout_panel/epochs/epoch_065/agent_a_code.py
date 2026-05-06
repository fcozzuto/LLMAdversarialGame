def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    # Choose a resource the opponent is currently advantaged on (meant to intercept / contest).
    best_target = None
    best_adv = -10**9
    for r in resources:
        if not r or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        dme = md(sx, sy, rx, ry)
        dop = md(ox, oy, rx, ry)
        if dme == 0:
            adv = 10**6  # we're already on it
        else:
            # Prefer resources where opponent is closer; break ties by closeness to center and smaller dop.
            adv = (dme - dop) * -1 + (-(abs(rx - cx) + abs(ry - cy))) * 0.01 + (-dop) * 0.001
        if adv > best_adv:
            best_adv = adv
            best_target = (rx, ry)

    if not best_target:
        return [0, 0]

    rx, ry = best_target
    # Score each move by: (1) can we reach the target sooner, (2) deny by increasing opponent distance,
    # (3) small center pull to avoid getting stuck.
    best_score = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        dme2 = md(nx, ny, rx, ry)
        dop2 = md(ox, oy, rx, ry)  # opponent position unchanged this turn
        # Intercept objective: reduce distance to target; also discourage staying away from contested resource.
        s = 0.0
        if dme2 == 0:
            s += 1e7
        else:
            s += 10000.0 / (dme2 + 1)
        # Deny: if opponent is closer, try to make our future distance better than theirs after move.
        s += (md(ox, oy, rx, ry) - dme2) * 2.0
        # Opponent separation (slight): move to increase distance to opponent while contesting.
        s += (md(nx, ny, ox, oy)) * 0.05
        # Center pull (tiny)
        s += (-(abs(nx - cx) + abs(ny - cy))) * 0.01

        if best_score is None or s > best_score or (s == best_score and (dx, dy) < best_move):
            best_score = s
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]