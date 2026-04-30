def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        resources = [(sx, sy)]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = (0, 0)
    best_score = -10**9
    my = (sx, sy)
    opp = (ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        cand = (nx, ny)

        # Find best target advantage: (opp_dist - self_dist) favors winning cells.
        best_adv = -10**9
        best_res = None
        for r in resources:
            d_self = cheb(cand, r)
            d_opp = cheb(opp, r)
            adv = d_opp - d_self
            if adv > best_adv:
                best_adv = adv
                best_res = r
            elif adv == best_adv and (best_res is None or manh(cand, r) < manh(cand, best_res)):
                best_res = r

        # Extra tie-breakers: prefer moving toward chosen resource, keep away from opponent if not ahead.
        d_self_to = cheb(cand, best_res) if best_res is not None else cheb(cand, my)
        d_opp_to = cheb(opp, best_res) if best_res is not None else cheb(opp, my)
        closer = d_opp_to - d_self_to

        # If opponent is already closer (adv small/negative), use a small repulsion to avoid handing them momentum.
        repulse = 0
        if closer <= 0:
            repulse = -manh(cand, opp)

        # Deterministic preference ordering via score, then move order implicitly by strict > only.
        score = 1000 * best_adv - 3 * d_self_to + 5 * (closer) + repulse
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move