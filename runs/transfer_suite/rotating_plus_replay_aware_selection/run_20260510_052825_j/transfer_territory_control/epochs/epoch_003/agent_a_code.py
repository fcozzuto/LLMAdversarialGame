def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation.get("opponent_position", (x, y))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    my_has = len(selfT) > 0
    opp_has = len(oppT) > 0

    # Choose a deterministic "focus" target direction: nearest unclaimed, else nearest opp territory
    if unclaimed:
        targets = list(unclaimed)
    elif opp_has:
        targets = list(oppT)
    else:
        targets = [(ox, oy)]
    focus = min(targets, key=lambda t: (cheb((x, y), t), (t[0], t[1])))

    best_move = (0, 0)
    best_score = -10**18
    # Mild variation by turn index to avoid local oscillation
    jitter = observation.get("turn_index", 0) % 3

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        pos = (nx, ny)

        score = 0
        if pos in oppT:
            score += 1200  # immediate swing by flipping
        elif pos in unclaimed:
            score += 220
        elif pos in selfT:
            score += 30

        d_focus = cheb(pos, focus)
        d_opp = cheb(pos, (ox, oy))
        d_me = cheb(pos, (x, y))

        # Expand toward focus while staying relatively far from opponent to reduce counterclaim risk
        score += 80 * (-d_focus)
        score += 12 * (d_opp)
        score += 3 * (1 if d_me > 0 else 0)

        # Prefer "frontier" moves: cells adjacent to unclaimed or opponent territory
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                    if (tx, ty) in unclaimed:
                        adj += 2
                    if (tx, ty) in oppT:
                        adj += 3
                    if (tx, ty) in selfT:
                        adj -= 1
        score += adj

        # Deterministic tie-break (and slight jitter)
        score += (jitter * 0.001) + (nx * 1e-6) + (ny * 1e-9)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]