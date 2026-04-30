def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # If no resources, run deterministically: maximize distance from opponent.
    if not resources:
        best = None
        for dx, dy, nx, ny in legal:
            v = cheb(nx, ny, ox, oy)
            cand = (v, -nx, -ny, dx, dy)
            if best is None or cand > best[0]:
                best = (cand, dx, dy)
        return [best[1], best[2]]

    res_set = set((int(x), int(y)) for x, y in resources)
    # Obstacle closeness penalty to avoid getting stuck near walls.
    def obst_pen(x, y):
        if not blocked: return 0
        mn = 10**9
        for bx, by in blocked:
            d = cheb(x, y, bx, by)
            if d < mn: mn = d
            if mn == 0: break
        return -0.6 / (1 + mn)

    # Target score: advantage on best resource after our move, with tie-breaks.
    best = None
    for dx, dy, nx, ny in legal:
        # Staying on a resource is heavily rewarded.
        on_res = 1.0 if (nx, ny) in res_set else 0.0
        # Our and opponent distances (opponent assumed to move next; we use current positions).
        best_adv = -10**9
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Prefer resources where we can beat opponent (opp_d - our_d).
            adv = (opp_d - our_d)
            # Small bias toward closer-to-target to reduce path length.
            adv -= 0.08 * our_d
            if adv > best_adv: best_adv = adv
        # Prefer progress away from our corner into open space and avoid opponent blocking.
        center_bias = -0.02 * cheb(nx, ny, (w - 1) // 2, (h - 1) // 2)
        opp_contact = 0.03 * (-cheb(nx, ny, ox, oy))
        cand = (on_res + best_adv + obst_pen(nx, ny) + center_bias + opp_contact, -nx, -ny, -dx, -dy)
        if best is None or cand > best[0]:
            best = (cand, dx, dy)

    return [int(best[1]), int(best[2])]