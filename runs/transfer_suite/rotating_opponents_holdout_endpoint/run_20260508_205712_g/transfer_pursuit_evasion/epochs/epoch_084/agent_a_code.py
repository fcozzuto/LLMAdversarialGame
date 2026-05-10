def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sp = observation["self_position"]
    op = observation["opponent_position"]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    sr = str(observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in sr) or ("hunter" in sr) or ("chaser" in sr)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def bfs(start):
        if not inb(start[0], start[1]):
            return None
        d = {(start[0], start[1]): 0}
        q = [(start[0], start[1])]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = d[(x, y)] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in d:
                    d[(nx, ny)] = nd
                    q.append((nx, ny))
        return d

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if opd is None or myd is None:
        return [0, 0]

    # If pursuer: move to minimize distance to opponent.
    # If evader: move to maximize distance from opponent, with a slight preference to stay safe locally.
    best = None
    best_val = None
    # Deterministic tie-break: prefer earlier moves in moves list.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if is_pursuer:
            val = opd.get((nx, ny), 10**9)
            better = (best is None) or (val < best_val)
        else:
            val = -opd.get((nx, ny), -10**9)
            # extra safety: if our next cell is closer to opponent in 1-step chebyshev, penalize
            cheb = max(abs(nx - ox), abs(ny - oy))
            cur_cheb = max(abs(sx - ox), abs(sy - oy))
            val = (val, 1 if cheb >= cur_cheb else 0, cheb)
            better = (best is None) or (val > best_val)
        if better:
            best = (nx, ny)
            best_val = val

    if best is None:
        return [0, 0]
    bx, by = best
    return [bx - sx, by - sy]