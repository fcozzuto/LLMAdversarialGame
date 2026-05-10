def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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
    if myd is None or opd is None:
        return [0, 0]

    if is_pursuer:
        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            dd = opd.get((nx, ny), 10**9)  # how quickly we reach opponent from here
            key = (dd, abs(nx - ox) + abs(ny - oy), ((nx + ny) & 1))
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [int(best[0]), int(best[1])] if best is not None else [0, 0]
    else:
        # Evader: run to farthest reachable cell from pursuer, but avoid stepping into near-capture positions.
        mypos = (sx, sy)
        fallback = [0, 0]
        farthest = None
        far_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            dist_from_pursuer = opd.get((nx, ny), -1)
            if dist_from_pursuer < 0:
                continue
            # Penalize positions that allow immediate pursuer adjacency (approx via dist 1)
            immediate = 0
            if dist_from_pursuer <= 1:
                immediate = 1
            key = (-dist_from_pursuer, immediate, abs(nx - ox) + abs(ny - oy), ((nx + ny) & 1))
            if far_key is None or key < far_key:
                far_key = key
                farthest = (dx, dy)
        return [int(farthest[0]), int(farthest[1])] if farthest is not None else fallback