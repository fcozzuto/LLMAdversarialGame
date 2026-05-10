def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    # pick a small deterministic set of promising targets (avoid large search)
    if unclaimed:
        ox, oy = observation["opponent_position"]
        def tgt_key(c):
            x, y = c
            near_opp = (0 if (x, y) in oppT else 1) + min(manh(x, y, *p) for p in ([(ox, oy)] if False else [(ox, oy)]))
            return man(x, y, sx, sy) * 2 + man(x, y, ox, oy) + (0 if (x, y) in oppT else 0) + (0 if (x, y) in selfT else 0) - (3 if (x, y) in unclaimed else 0) + near_opp
        # best-guess frontier: nearer to us, but also closer to opponent area
        targets = sorted(unclaimed, key=tgt_key)[:18]
    else:
        targets = []

    # if adjacent to opponent, prioritize direct flip
    adj_opp = []
    for dx, dy in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in oppT:
            adj_opp.append((dx, dy))
    if adj_opp:
        # tie-break deterministically toward reducing distance to opponent corner
        ox, oy = observation["opponent_position"]
        return min(adj_opp, key=lambda m: man(sx+m[0], sy+m[1], ox, oy))

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    ox, oy = observation["opponent_position"]
    opp_pos = (ox, oy)
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)
        val = 0
        if cell in oppT:
            val += 10**6
        elif cell in unclaimed:
            # acquiring neutral territory; also prefer cells closer to a good target
            if targets:
                val += 5000 - 50 * min(manh(nx, ny, tx, ty) for tx, ty in targets)
            else:
                val += 2000 - 20 * man(nx, ny, ox, oy)
        elif cell in selfT:
            val -= 5 * man(nx, ny, ox, oy) + 20
        else:
            val -= 100

        # avoid moving away from chosen targets; encourage frontier-ish moves
        if targets:
            val += -min(manh(nx, ny, tx, ty) for tx, ty in targets)

        # slight preference for progressing toward opponent side to enable future counterclaim
        val += -0.3 * man(nx, ny, *opp_pos)

        if val > best_val:
            best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]