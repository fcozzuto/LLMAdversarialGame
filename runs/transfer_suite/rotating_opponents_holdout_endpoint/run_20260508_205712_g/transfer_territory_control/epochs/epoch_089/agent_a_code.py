def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    unclaimed_set = []
    for c in unclaimed:
        if c and len(c) >= 2 and c[0] is not None and c[1] is not None:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                unclaimed_set.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def nearest_dist(x, y):
        if not unclaimed_set:
            return abs(ox - x) + abs(oy - y)
        best = 10**9
        for ux, uy in unclaimed_set:
            d = abs(ux - x) + abs(uy - y)
            if d < best:
                best = d
        return best if best != 10**9 else 0

    best_move = [0, 0]
    best_score = -10**18
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d_target = nearest_dist(nx, ny)
            d_opp = abs(ox - nx) + abs(oy - ny)
            score = -d_target + 0.15 * d_opp
            if score > best_score or (score == best_score and (dx, dy) == (0, 0)):
                best_score = score
                best_move = [dx, dy]
    return best_move