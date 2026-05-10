def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [7, 7]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                s.add((int(p[0]), int(p[1])))
        return s

    blocks = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def adj8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny):
                    yield nx, ny

    opp_front = []
    for cx, cy in unclaimed:
        for nx, ny in adj8(cx, cy):
            if (nx, ny) in opp_terr:
                opp_front.append((cx, cy))
                break

    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_sc = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocks:
            nx, ny = sx, sy

        score = 0
        if (nx, ny) in opp_terr:
            score += 60
        elif (nx, ny) in unclaimed:
            score += 22
        elif (nx, ny) in self_terr:
            score += 8
        else:
            score += 2

        # Prefer approaching opponent front; otherwise approach opponent position.
        if opp_front:
            d = min(manh((nx, ny), c) for c in opp_front)
            score += (25 - min(25, d)) * 2
        else:
            d = man((nx, ny), (ox, oy))
            score += (18 - min(18, d))

        # Avoid stepping adjacent to obstacles/edges less, but also discourage being too exposed to opponent.
        expose = 0
        for ax, ay in adj8(nx, ny):
            if (ax, ay) in opp_terr:
                expose += 1
        score -= expose * 3

        if score > best_sc or (score == best_sc and (dx, dy) < best_move):
            best_sc = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]