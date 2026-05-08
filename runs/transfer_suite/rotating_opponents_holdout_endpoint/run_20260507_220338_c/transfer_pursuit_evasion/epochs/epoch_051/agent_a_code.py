def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    scores = observation.get("scores") or {}
    my_score = None
    opp_score = None
    if isinstance(scores, dict):
        for k in ("self", "me", "agent", "player", "p1"):
            if k in scores:
                my_score = scores[k]
                break
        for k in ("opponent", "them", "enemy", "p2"):
            if k in scores:
                opp_score = scores[k]
                break
    if my_score is None or opp_score is None:
        my_score = 0
        opp_score = 0

    role_s = str(observation.get("self_role", "")).lower()
    wants_capture = any(k in role_s for k in ("purs", "catch", "capture", "hunter", "seeker", "chase"))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x, y):
        dx = abs(ox - x)
        dy = abs(oy - y)
        return dx if dx > dy else dy

    def move_score(nx, ny, dx, dy):
        if nx == ox and ny == oy:
            return 10**9 if wants_capture else -10**9
        d = cheb(nx, ny)
        s = -d * 1000
        if wants_capture:
            s += -d
        else:
            s += d
        s += -((ox - nx) * dx + (oy - ny) * dy) * 2
        if (nx, ny) in blocked:
            s -= 10**8
        return s

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    target = wants_capture or (my_score >= opp_score)
    best_move = moves[4]
    best_val = -10**18 if target else 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        val = move_score(nx, ny, dx, dy)
        if target:
            if val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val, best_move = val, (dx, dy)
        else:
            if val < best_val or (val == best_val and (dx, dy) < best_move):
                best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]