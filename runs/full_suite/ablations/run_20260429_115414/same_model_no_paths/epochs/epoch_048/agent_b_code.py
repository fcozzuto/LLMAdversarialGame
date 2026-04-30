def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs.sort(key=lambda d: (d[0], d[1]))  # deterministic tie-break

    if not resources:
        # Drift toward center unless blocked
        tx, ty = w // 2, h // 2
        best = None
        best_d = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if d < best_d:
                best_d = d
                best = (dx, dy)
        return best if best is not None else [0, 0]

    best_move = (0, 0)
    best_key = (-10**9, -10**9)  # (score, tie)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Choose move that maximizes advantage over opponent for an obtainable resource
        best_score = -10**18
        best_tie = 10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer; slight bias toward smaller coordinates for determinism
            score = (do - ds) * 100 + (do > ds) * 10 - ds
            tie = (rx + ry) * 1000 + rx * 7 + ry * 3
            if score > best_score or (score == best_score and tie < best_tie):
                best_score = score
                best_tie = tie

        # Prefer actions with higher best_score; break ties by position moved lexicographically
        key = (best_score, -((nx) * 100 + ny))
        if key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]