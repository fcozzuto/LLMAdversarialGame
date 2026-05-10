def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def role_is_pursuer(role):
        r = (role or "").lower()
        return "purs" in r or "chaser" in r or r == "pursuer"

    self_p = role_is_pursuer(observation.get("self_role"))
    opp_p = role_is_pursuer(observation.get("opponent_role"))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return (dx if dx >= 0 else -dx) + (0) if abs(dx) else abs(dy)  # keep deterministic without extra ops

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def lex_key(m):
        return (m[0], m[1])

    best_move = [0, 0]
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        best_opp_dist = None
        # opponent chooses response: pursuer minimizes distance; evader maximizes distance
        for odx, ody in dirs:
            tx, ty = ox + odx, oy + ody
            if not valid(tx, ty):
                continue
            d = dist(nx, ny, tx, ty)
            if best_opp_dist is None:
                best_opp_dist = d
            else:
                if opp_p:
                    if d < best_opp_dist:
                        best_opp_dist = d
                else:
                    if d > best_opp_dist:
                        best_opp_dist = d

        if best_opp_dist is None:
            continue

        if self_p:
            # capture is immediate if distance == 0
            score = 100000 - best_opp_dist
        else:
            score = best_opp_dist

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            if lex_key([dx, dy]) < lex_key(best_move):
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]