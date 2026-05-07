def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in blocked:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    def man(a, b, c, d): return abs(a - c) + abs(b - d)

    def opp_step(tx, ty, px, py):
        best = None
        bestd = None
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                continue
            d = man(nx, ny, tx, ty)
            if best is None or d < bestd or (d == bestd and (dx * dx + dy * dy) < (best[0] * best[0] + best[1] * best[1])):
                best = (dx, dy)
                bestd = d
        return best if best is not None else (0, 0)

    # Pick target that maximizes expected lead (self advantage minus opponent).
    best_t = None
    best_s = None
    for tx, ty in resources:
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        # Slightly prioritize nearer resources; and prefer positions where we can create/keep a lead.
        s = (od - sd) * 10 - sd
        if best_t is None or s > best_s:
            best_t = (tx, ty)
            best_s = s
    tx, ty = best_t

    # One-ply lookahead: choose move that maximizes (opponent_dist_next - self_dist_next).
    best_move = None
    best_val = None
    best_selfd = None
    for dx, dy in legal:
        nsx, nsy = sx + dx, sy + dy
        # If we'd land on the resource, consider it strongly.
        self_d = man(nsx, nsy, tx, ty)
        od_next_dx, od_next_dy = opp_step(tx, ty, ox, oy)
        nox, noy = ox + od_next_dx, oy + od_next_dy
        opp_d = man(nox, noy, tx, ty)
        val = (opp_d - self_d) * 10 - self_d
        if best_move is None or val > best_val or (val == best_val and (best_selfd is None or self_d < best_selfd)):
            best_move = (dx, dy)
            best_val = val
            best_selfd = self_d

    return [int(best_move[0]), int(best_move[1])]