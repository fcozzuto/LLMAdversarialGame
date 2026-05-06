def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in blocked
    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not legal(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    targets = []
    for r in resources:
        if isinstance(r, dict):
            pos = r.get("position")
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                targets.append((pos[0], pos[1]))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            targets.append((r[0], r[1]))

    center = (w // 2, h // 2)
    mypos = (sx, sy)
    opp = (ox, oy)

    best_t = None
    best_adv = -10**9
    for t in targets:
        if not legal(t[0], t[1]): 
            continue
        dself = man(mypos, t)
        dopp = man(opp, t)
        adv = dopp - dself
        if adv > best_adv or (adv == best_adv and dself < man(mypos, best_t) if best_t else True):
            best_adv, best_t = adv, t

    if best_t is None or best_adv < 0:
        best_t = center

    # choose move: reduce distance to chosen target; if tie, increase distance from opponent
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_to = man((nx, ny), best_t)
        d_opp = man((nx, ny), opp)
        val = -d_to + 0.001 * d_opp
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val, best_move = val, (dx, dy)
    return [best_move[0], best_move[1]]