def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = (0, 0)
    best_score = -10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        min_d = 10**9
        close_cnt = 0
        band_bonus = 0
        opp_aware = 0

        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = int(r[0]), int(r[1])
            d0 = man(sx, sy, rx, ry)
            d1 = man(nx, ny, rx, ry)
            if d1 < min_d:
                min_d = d1
            if d1 <= 2:
                close_cnt += 1
            if ry == oy:
                band_bonus += 3
            if d1 < d0:
                opp_aware += 1

        # Prefer: getting closer to nearest resource, staying near several, and resources on opponent's current y-band
        score = (-2.5 * min_d) + (1.2 * close_cnt) + (0.8 * band_bonus) + (0.3 * opp_aware)

        if (nx, ny) == (ox, oy):
            score -= 2.0  # mild deterrent to overlap

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]