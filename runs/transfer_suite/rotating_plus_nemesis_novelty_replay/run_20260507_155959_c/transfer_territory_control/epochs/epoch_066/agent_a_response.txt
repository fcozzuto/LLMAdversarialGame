def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs
    def neighbors(x, y):
        return [(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]

    self_t = set((int(c[0]), int(c[1])) for c in (observation.get("self_territory") or []) if c is not None and len(c) >= 2)
    opp_t = set((int(c[0]), int(c[1])) for c in (observation.get("opponent_territory") or []) if c is not None and len(c) >= 2)
    unclaimed = set((int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c is not None and len(c) >= 2)

    if not unclaimed:
        return [0, 0]

    # Pick target unclaimed cell that likely expands/blocks us vs opponent.
    best_target = None
    best_val = -10**9
    for tx, ty in unclaimed:
        adj_self = sum((nx, ny) in self_t for nx, ny in neighbors(tx, ty))
        adj_opp = sum((nx, ny) in opp_t for nx, ny in neighbors(tx, ty))
        # Prefer near ourselves; heavily prefer adjacent-to-self expansion.
        val = (12 * adj_self - 9 * adj_opp) - (abs(tx - sx) + abs(ty - sy))
        if val > best_val or (val == best_val and (tx, ty) < best_target):
            best_val = val
            best_target = (tx, ty)

    tx, ty = best_target

    # Choose move that heads towards target with local advantage against opponent.
    move_order = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dist = abs(tx - nx) + abs(ty - ny)
        # Small bias to expand onto our advantageous territory (entering opponent territory flips control).
        enter_opp = (nx, ny) in opp_t
        adj_self = sum((px, py) in self_t for px, py in neighbors(nx, ny))
        adj_opp = sum((px, py) in opp_t for px, py in neighbors(nx, ny))
        score = -dist + (6 if enter_opp else 0) + (2 * adj_self - 2 * adj_opp)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]